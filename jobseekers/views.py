# jobseekers/views.py

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.views.generic import TemplateView, CreateView, UpdateView
from django.urls import reverse_lazy, reverse
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import DetailView, ListView
from employers.models import Application, Vacancy
from core_models.models import Skill
from .forms import JobseekerProfileForm
from .models import JobseekerProfile, Education, Experience, JobseekerSkill
from django.db.models import Q, Value, DecimalField


# === ЛИЧНЫЙ КАБИНЕТ ===
class JobseekerCabinetView(LoginRequiredMixin, TemplateView):
    template_name = 'jobseekers/cabinet.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile, _ = JobseekerProfile.objects.get_or_create(user=self.request.user)
        context['profile'] = profile
        context['education_list'] = profile.education.all()
        context['experience_list'] = profile.experience.all()
        context['skill_list'] = profile.skills.select_related('skill').all()
        context['all_skills'] = Skill.objects.all()
        return context


# === РЕДАКТИРОВАНИЕ ОСНОВНОЙ ИНФОРМАЦИИ (ГЛАВНОЕ!) ===
class JobseekerProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = JobseekerProfile
    form_class = JobseekerProfileForm  # ← ОБЯЗАТЕЛЬНО!
    template_name = 'jobseekers/profile_edit.html'

    # success_url на случай, если reverse_lazy не сработает (иногда бывает)
    def get_success_url(self):
        return reverse('jobseekers:cabinet')

    def get_object(self, queryset=None):
        """Получаем или создаём профиль текущего пользователя"""
        profile, created = JobseekerProfile.objects.get_or_create(user=self.request.user)
        return profile

    def form_valid(self, form):
        """Вызывается при валидной форме — сохраняем и показываем сообщение"""
        messages.success(self.request, "Резюме успешно обновлено!")
        return super().form_valid(form)

    def form_invalid(self, form):
        """Если форма невалидна — покажем ошибки"""
        messages.error(self.request, "Проверьте правильность заполнения полей")
        return super().form_invalid(form)


# === МОИ ОТКЛИКИ ===
class MyApplicationsView(LoginRequiredMixin, TemplateView):
    template_name = 'jobseekers/my_applications.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile, _ = JobseekerProfile.objects.get_or_create(user=self.request.user)
        context['applications'] = Application.objects.filter(
            jobseeker=profile
        ).select_related('vacancy__company', 'vacancy').order_by('-applied_at')
        return context


# === ОПЫТ РАБОТЫ ===
class ExperienceCreateView(LoginRequiredMixin, CreateView):
    model = Experience
    fields = ['company', 'position', 'description', 'start_date', 'end_date', 'is_current']
    template_name = 'jobseekers/experience_form.html'   # ← ИСПРАВЛЕНО
    success_url = reverse_lazy('jobseekers:cabinet')

    def form_valid(self, form):
        profile, _ = JobseekerProfile.objects.get_or_create(user=self.request.user)
        form.instance.profile = profile
        return super().form_valid(form)


# === ОБРАЗОВАНИЕ ===
class EducationCreateView(LoginRequiredMixin, CreateView):
    model = Education
    fields = ['institution', 'faculty', 'specialty', 'degree', 'start_year', 'end_year', 'is_current']
    template_name = 'jobseekers/education_form.html'   # ← ИСПРАВЛЕНО
    success_url = reverse_lazy('jobseekers:cabinet')

    def form_valid(self, form):
        profile, _ = JobseekerProfile.objects.get_or_create(user=self.request.user)
        form.instance.profile = profile
        return super().form_valid(form)


class ResumeDetailView(DetailView):
    model = JobseekerProfile
    template_name = 'jobseekers/resume_detail.html'
    slug_field = 'user__username'
    slug_url_kwarg = 'username'
    context_object_name = 'profile'

    def get_queryset(self):
        return JobseekerProfile.objects.select_related('user').prefetch_related('experience', 'education',
                                                                                'skills__skill')


class ResumeListView(ListView):
    model = JobseekerProfile
    template_name = 'jobseekers/resume_list.html'
    context_object_name = 'profiles'
    paginate_by = 12

    def get_queryset(self):
        qs = JobseekerProfile.objects.select_related('user').prefetch_related('skills__skill')

        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(user__first_name__icontains=q) |
                Q(user__last_name__icontains=q) |
                Q(user__username__icontains=q) |
                Q(desired_position__icontains=q) |
                Q(about__icontains=q)
            )

        salary_from = self.request.GET.get('salary_from')
        if salary_from and salary_from.isdigit():
            salary = int(salary_from)
            qs = qs.annotate(
                salary_effective=Coalesce(
                    'desired_salary_from',
                    Value(0, output_field=DecimalField(max_digits=10, decimal_places=2))
                )
            ).filter(salary_effective__gte=salary)

        skill_id = self.request.GET.get('skill')
        if skill_id and skill_id.isdigit():
            qs = qs.filter(skills__skill_id=skill_id)

        return qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['skills'] = Skill.objects.all()[:30]
        return context


class ApplyVacancyView(LoginRequiredMixin, View):
    """
    Отклик на вакансию — простая, надёжная, без HTMX
    """

    def post(self, request, pk):
        vacancy = get_object_or_404(Vacancy, pk=pk, is_active=True)

        # Получаем или создаём профиль соискателя
        profile, created = JobseekerProfile.objects.get_or_create(
            user=request.user
        )

        # Проверяем, не откликался ли уже
        if Application.objects.filter(vacancy=vacancy, jobseeker=profile).exists():
            messages.warning(request, "Вы уже откликнулись на эту вакансию!")
        else:
            Application.objects.create(
                vacancy=vacancy,
                jobseeker=profile
            )
            messages.success(request, "Ваш отклик успешно отправлен!")

        # Возвращаемся туда, откуда пришли (или на вакансию)
        referrer = request.META.get('HTTP_REFERER')
        if referrer:
            return redirect(referrer)
        return redirect('employers:vacancy_detail', pk=vacancy.pk)


def remove_experience(request, experience_id):
    if request.user.is_authenticated:
        profile, _ = JobseekerProfile.objects.get_or_create(user=request.user)
        Experience.objects.filter(profile=profile, id=experience_id).delete()
    return redirect('jobseekers:cabinet')


def remove_education(request, education_id):
    if request.user.is_authenticated:
        profile, _ = JobseekerProfile.objects.get_or_create(user=request.user)
        Education.objects.filter(profile=profile, id=education_id).delete()
    return redirect('jobseekers:cabinet')


def remove_skill(request, skill_id):
    if request.user.is_authenticated:
        profile, _ = JobseekerProfile.objects.get_or_create(user=request.user)
        JobseekerSkill.objects.filter(profile=profile, skill_id=skill_id).delete()
    return redirect('jobseekers:cabinet')


# ДОБАВЛЕНИЕ навыка — теперь обычная форма с редиректом
def add_skill(request):
    if request.method == "POST" and request.user.is_authenticated:
        profile, _ = JobseekerProfile.objects.get_or_create(user=request.user)
        skill_id = request.POST.get('skill_id')
        level = request.POST.get('level', 2)

        if skill_id:
            skill = get_object_or_404(Skill, id=skill_id)
            JobseekerSkill.objects.update_or_create(
                profile=profile, skill=skill, defaults={'level': level}
            )

    return redirect('jobseekers:cabinet')  # ← перезагружаем страницу