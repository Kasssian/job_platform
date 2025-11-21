from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView

from core_models.models import Category
from .models import Company, Vacancy, Application


class CompanyProfileView(LoginRequiredMixin, DetailView):
    model = Company
    template_name = 'employers/company_profile.html'
    context_object_name = 'company'

    def get_object(self):
        return get_object_or_404(Company, user=self.request.user)


class CompanyUpdateView(LoginRequiredMixin, UpdateView):
    model = Company
    fields = ['name', 'description', 'logo', 'website', 'address',
              'founded_year', 'employees_count']
    template_name = 'employers/company_form.html'
    success_url = reverse_lazy('employes:company_profile')

    def get_object(self):
        return get_object_or_404(Company, user=self.request.user)


class VacancyListView(ListView):
    model = Vacancy
    template_name = 'employers/vacancy_list.html'
    context_object_name = 'vacancies'
    paginate_by = 12

    def get_queryset(self):
        qs = Vacancy.objects.filter(is_active=True).select_related(
            'company__user', 'category'
        )

        # Фильтры
        query = self.request.GET.get('q')
        category_id = self.request.GET.get('category')
        location = self.request.GET.get('location')
        salary_min = self.request.GET.get('salary_min')

        if query:
            qs = qs.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(requirements__icontains=query)
            )
        if category_id:
            qs = qs.filter(category_id=category_id)
        if location:
            qs = qs.filter(location__icontains=location)
        if salary_min:
            qs = qs.filter(salary_from__gte=salary_min)

        return qs.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class VacancyDetailView(DetailView):
    model = Vacancy
    template_name = 'employers/vacancy_detail.html'
    context_object_name = 'vacancy'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vacancy = self.object
        context['applications'] = Application.objects.filter(
            vacancy=vacancy
        ).select_related('jobseeker__user').order_by('-applied_at')
        context['can_apply'] = (self.request.user.is_authenticated and
                                hasattr(self.request.user, 'jobseeker_profile') and
                                not Application.objects.filter(
                                    vacancy=vacancy,
                                    jobseeker=self.request.user.jobseeker_profile
                                ).exists())
        return context


class VacancyCreateView(LoginRequiredMixin, CreateView):
    model = Vacancy
    fields = ['title', 'description', 'requirements', 'responsibilities',
              'salary_from', 'salary_to', 'location', 'category', 'is_active']
    template_name = 'employers/vacancy_form.html'
    success_url = reverse_lazy('employes:employer_cabinet')

    def form_valid(self, form):
        company = get_object_or_404(Company, user=self.request.user)
        form.instance.company = company
        messages.success(self.request, 'Вакансия успешно создана!')
        return super().form_valid(form)


class VacancyUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Vacancy
    fields = ['title', 'description', 'requirements', 'responsibilities',
              'salary_from', 'salary_to', 'location', 'category', 'is_active']
    template_name = 'employers/vacancy_form.html'

    def test_func(self):
        vacancy = self.get_object()
        return (vacancy.company.user == self.request.user or
                self.request.user.is_staff)

    def get_success_url(self):
        return reverse_lazy('employes:vacancy_detail', kwargs={'pk': self.object.pk})


class VacancyDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Vacancy
    success_url = reverse_lazy('employes:employer_cabinet')

    def test_func(self):
        vacancy = self.get_object()
        return (vacancy.company.user == self.request.user or
                self.request.user.is_staff)

    def get(self, request, *args, **kwargs):
        messages.warning(request, 'Вакансия удалена')
        return super().get(request, *args, **kwargs)


class EmployerCabinetView(LoginRequiredMixin, TemplateView):
    template_name = 'employers/cabinet.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = get_object_or_404(Company, user=self.request.user)

        context['company'] = company
        context['vacancies'] = Vacancy.objects.filter(company=company).order_by('-created_at')
        context['total_applications'] = Application.objects.filter(
            vacancy__company=company
        ).count()
        context['new_applications'] = Application.objects.filter(
            vacancy__company=company,
            status='sent'
        ).count()

        return context


class VacancyApplicationsView(LoginRequiredMixin, ListView):
    model = Application
    template_name = 'employers/applications.html'
    context_object_name = 'applications'
    paginate_by = 15

    def get_queryset(self):
        company = get_object_or_404(Company, user=self.request.user)
        return Application.objects.filter(
            vacancy__company=company
        ).select_related(
            'jobseeker__user', 'vacancy'
        ).order_by('-applied_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vacancy_filter'] = self.kwargs.get('vacancy_id')
        return context


# HTMX: изменить статус отклика
def htmx_update_application_status(request, application_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Авторизация требуется'}, status=401)

    application = get_object_or_404(Application, id=application_id)
    company = get_object_or_404(Company, user=request.user)

    if application.vacancy.company != company and not request.user.is_staff:
        return JsonResponse({'error': 'Нет доступа'}, status=403)

    new_status = request.POST.get('status')
    if new_status in ['sent', 'viewed', 'interview', 'rejected', 'hired']:
        application.status = new_status
        application.save()

        # Создать уведомление
        from core_models.models import Notification
        Notification.objects.create(
            user=application.jobseeker.user,
            title=f'Статус отклика изменён',
            message=f'Ваш отклик на вакансию "{application.vacancy.title}" теперь: {application.get_status_display()}'
        )

        return JsonResponse({
            'success': True,
            'status': application.get_status_display()
        })

    return JsonResponse({'error': 'Неверный статус'}, status=400)
