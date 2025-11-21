from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q

from employers.models import Application
from core_models.models import User, Category, Skill
from .models import JobseekerProfile, Education, Experience, JobseekerSkill


class JobseekerProfileView(LoginRequiredMixin, DetailView):
    model = JobseekerProfile
    template_name = 'jobseekers/profile.html'
    context_object_name = 'profile'

    def get_object(self):
        return get_object_or_404(JobseekerProfile, user=self.request.user)


class JobseekerProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = JobseekerProfile
    fields = ['about', 'desired_position', 'desired_salary_from', 'desired_salary_to',
              'experience_years', 'is_open_to_work']
    template_name = 'jobseekers/profile_form.html'
    success_url = reverse_lazy('jobseekers:profile')

    def get_object(self):
        return get_object_or_404(JobseekerProfile, user=self.request.user)


class EducationCreateView(LoginRequiredMixin, CreateView):
    model = Education
    fields = ['institution', 'faculty', 'specialty', 'degree', 'start_year',
              'end_year', 'is_current']
    template_name = 'jobseekers/education_form.html'
    success_url = reverse_lazy('jobseekers:profile')

    def form_valid(self, form):
        profile = get_object_or_404(JobseekerProfile, user=self.request.user)
        form.instance.profile = profile
        return super().form_valid(form)


class ExperienceCreateView(LoginRequiredMixin, CreateView):
    model = Experience
    fields = ['company', 'position', 'description', 'start_date', 'end_date', 'is_current']
    template_name = 'jobseekers/experience_form.html'
    success_url = reverse_lazy('jobseekers:profile')

    def form_valid(self, form):
        profile = get_object_or_404(JobseekerProfile, user=self.request.user)
        form.instance.profile = profile
        return super().form_valid(form)


class JobseekerCabinetView(LoginRequiredMixin, TemplateView):
    template_name = 'jobseekers/cabinet.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = get_object_or_404(JobseekerProfile, user=self.request.user)

        context['profile'] = profile
        context['education'] = profile.education.all()
        context['experience'] = profile.experience.all()
        context['skills'] = profile.skills.select_related('skill')
        context['applications'] = Application.objects.filter(
            jobseeker=profile
        ).select_related('vacancy__company__user').order_by('-applied_at')

        return context


class MyApplicationsView(LoginRequiredMixin, ListView):
    model = Application
    template_name = 'jobseekers/applications.html'
    context_object_name = 'applications'
    paginate_by = 10

    def get_queryset(self):
        profile = get_object_or_404(JobseekerProfile, user=self.request.user)
        return Application.objects.filter(jobseeker=profile).select_related(
            'vacancy__company'
        ).order_by('-applied_at')


# HTMX: добавить навык
def htmx_add_skill(request):
    if request.method == 'POST':
        profile = get_object_or_404(JobseekerProfile, user=request.user)
        skill_id = request.POST.get('skill_id')
        level = request.POST.get('level', 2)

        skill = get_object_or_404(Skill, id=skill_id)

        if not JobseekerSkill.objects.filter(profile=profile, skill=skill).exists():
            JobseekerSkill.objects.create(
                profile=profile,
                skill=skill,
                level=level
            )

        return JsonResponse({'success': True})

    return JsonResponse({'error': 'Bad request'}, status=400)


# HTMX: отклик на вакансию
def htmx_apply_vacancy(request, vacancy_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Требуется авторизация'}, status=401)

    profile = get_object_or_404(JobseekerProfile, user=request.user)
    vacancy = get_object_or_404('employes.Vacancy', id=vacancy_id, is_active=True)

    if Application.objects.filter(jobseeker=profile, vacancy=vacancy).exists():
        return JsonResponse({'error': 'Вы уже откликнулись на эту вакансию'}, status=400)

    application = Application.objects.create(
        jobseeker=profile,
        vacancy=vacancy,
        cover_letter=request.POST.get('cover_letter', '')
    )

    return JsonResponse({
        'success': True,
        'message': 'Отклик отправлен!',
        'application_id': application.id
    })