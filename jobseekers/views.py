import io
from datetime import timezone

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from xhtml2pdf import pisa

from .forms import ResumeForm
from .models import Resume, Application


class ResumeListView(ListView):
    model = Resume
    template_name = 'jobseekers/resume_list.html'
    context_object_name = 'resumes'
    paginate_by = 15


class ResumeDetailView(DetailView):
    model = Resume
    template_name = 'jobseekers/resume_detail.html'


class ResumeCreateView(LoginRequiredMixin, CreateView):
    model = Resume
    form_class = ResumeForm
    template_name = 'jobseekers/resume_form.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user.profile
        messages.success(self.request, 'Резюме успешно создано!')
        return super().form_valid(form)


class ResumeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Resume
    form_class = ResumeForm
    template_name = 'jobseekers/resume_form.html'

    def test_func(self):
        return self.get_object().owner == self.request.user.profile


class ResumeDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Resume
    template_name = 'jobseekers/resume_confirm_delete.html'
    success_url = reverse_lazy('jobseekers:my_cabinet')

    def test_func(self):
        return self.get_object().owner == self.request.user.profile


class JobSeekerCabinetView(LoginRequiredMixin, TemplateView):
    template_name = 'jobseekers/cabinet.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.request.user.profile
        context['resumes'] = Resume.objects.filter(owner=profile)
        context['applications'] = Application.objects.filter(resume__owner=profile).select_related('vacancy')
        return context


# HTMX: отклик на вакансию
def htmx_apply_vacancy(request, vacancy_id):
    if not request.user.is_authenticated or request.user.profile.role != 'job_seeker':
        return JsonResponse({'error': 'Доступ запрещён'}, status=403)

    resume_id = request.POST.get('resume_id')
    resume = get_object_or_404(Resume, id=resume_id, owner=request.user.profile)
    vacancy = get_object_or_404('employers.Vacancy', id=vacancy_id, is_active=True)

    if Application.objects.filter(resume=resume, vacancy=vacancy).exists():
        return JsonResponse({'error': 'Вы уже откликались'}, status=400)

    Application.objects.create(resume=resume, vacancy=vacancy)
    return JsonResponse({
        'success': True,
        'message': 'Отклик отправлен!'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_resume_pdf(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id)

    # Проверка: работодатель может скачать любое резюме
    if not request.user.role == 'employer':  # предполагаем, что у User есть поле role
        return Response({"detail": "Только работодатели могут скачивать резюме"}, status=403)

    template = get_template('resume_pdf.html')
    html = template.render({'resume': resume, 'now': timezone.now()})

    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)

    if not pdf.err:
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Резюме_{resume.full_name.replace(" ", "_")}.pdf"'
        response.write(result.getvalue())
        return response

    return Response({"detail": "Ошибка генерации PDF"}, status=500)
