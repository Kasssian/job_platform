# employes/views.py
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib import messages
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from core_models.models import Category, Skill
from .models import Company, Vacancy, Application
from .forms import CompanyForm, VacancyForm
from .serializers import CompanySerializer, VacancySerializer, ApplicationSerializer


# HTML Views
class VacancyListView(ListView):
    model = Vacancy
    template_name = 'employes/vacancy_list.html'
    context_object_name = 'vacancies'
    paginate_by = 12

    def get_queryset(self):
        qs = Vacancy.objects.filter(is_active=True).select_related('company__user', 'category')
        q = self.request.GET.get('q')
        cat = self.request.GET.get('category')
        loc = self.request.GET.get('location')
        skill = self.request.GET.get('skill')

        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
        if cat:
            qs = qs.filter(category_id=cat)
        if loc:
            qs = qs.filter(location__icontains=loc)
        if skill:
            qs = qs.filter(skills__name=skill)

        return qs.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['skills'] = Skill.objects.all()
        return context


class VacancyDetailView(DetailView):
    model = Vacancy
    template_name = 'employes/vacancy_detail.html'
    context_object_name = 'vacancy'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated and self.request.user.role == 'jobseeker':
            profile = get_object_or_404(JobseekerProfile, user=self.request.user)
            context['can_apply'] = not Application.objects.filter(jobseeker=profile, vacancy=self.object).exists()
        return context


class VacancyCreateView(LoginRequiredMixin, CreateView):
    model = Vacancy
    form_class = VacancyForm
    template_name = 'employes/vacancy_form.html'

    def form_valid(self, form):
        company = get_object_or_404(Company, user=self.request.user)
        form.instance.company = company
        messages.success(self.request, 'Вакансия создана!')
        return super().form_valid(form)


class VacancyUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Vacancy
    form_class = VacancyForm
    template_name = 'employes/vacancy_form.html'

    def test_func(self):
        return self.get_object().company.user == self.request.user or self.request.user.is_staff


class VacancyDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Vacancy
    template_name = 'employes/vacancy_confirm_delete.html'
    success_url = reverse_lazy('employes:employer_cabinet')

    def test_func(self):
        return self.get_object().company.user == self.request.user or self.request.user.is_staff


class CompanyCreateView(LoginRequiredMixin, CreateView):
    model = Company
    form_class = CompanyForm
    template_name = 'employes/company_form.html'

    def form_valid(self, form):
        if self.request.user.role != 'employer':
            messages.error(self.request, 'Только работодатели могут создавать компанию.')
            return redirect('core_models:home')
        form.instance.user = self.request.user
        messages.success(self.request, 'Компания создана!')
        return super().form_valid(form)


class CompanyUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Company
    form_class = CompanyForm
    template_name = 'employes/company_form.html'

    def test_func(self):
        return self.get_object().user == self.request.user


class EmployerCabinetView(LoginRequiredMixin, TemplateView):
    template_name = 'employes/cabinet.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company = get_object_or_404(Company, user=self.request.user)
        context['company'] = company
        context['vacancies'] = Vacancy.objects.filter(company=company)
        context['applications'] = Application.objects.filter(vacancy__company=company).select_related('jobseeker__user')
        return context


# API Views (DRF)
class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Company.objects.all()
        return Company.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class VacancyViewSet(viewsets.ModelViewSet):
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsOwnerOrAdmin()]
        return []

    def perform_create(self, serializer):
        company = get_object_or_404(Company, user=self.request.user)
        serializer.save(company=company)


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'employer':
            return Application.objects.filter(vacancy__company__user=self.request.user)
        return Application.objects.filter(jobseeker__user=self.request.user)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        application = self.get_object()
        new_status = request.data.get('status')
        if new_status in dict(Application._meta.get_field('status').choices):
            application.status = new_status
            application.save()
            Notification.objects.create(
                user=application.jobseeker.user,
                title='Обновление статуса отклика',
                message=f'Статус вашего отклика на "{application.vacancy.title}" изменён на "{new_status}".'
            )
            return Response({'status': 'ok'})
        return Response({'error': 'Недопустимый статус'}, status=400)