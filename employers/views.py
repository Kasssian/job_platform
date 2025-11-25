from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Count, Exists, OuterRef, Value, BooleanField
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy, reverse
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView

from core_models.models import Category, Notification
from jobseekers.models import JobseekerProfile
from .Forms import VacancyForm
from .models import Company, Vacancy, Application
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from core_models.models import Notification

class CompanyProfileView(DetailView):
    model = Company
    template_name = 'employers/company_profile.html'
    context_object_name = 'company'
    pk_url_kwarg = 'company_id'  # будем использовать /company/5/

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vacancies = self.object.vacancies.filter(is_active=True)

        # === ДОБАВЛЯЕМ already_applied ===
        if self.request.user.is_authenticated and self.request.user.role == 'jobseeker':
            profile, _ = JobseekerProfile.objects.get_or_create(user=self.request.user)
            applied_ids = set(Application.objects.filter(jobseeker=profile).values_list('vacancy_id', flat=True))
            for v in vacancies:
                v.already_applied = v.pk in applied_ids
        else:
            for v in vacancies:
                v.already_applied = False

        context['active_vacancies'] = vacancies
        return context



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

        # === ДОБАВЛЯЕМ already_applied ===
        vacancy.already_applied = False
        if self.request.user.is_authenticated and self.request.user.role == 'jobseeker':
            profile, _ = JobseekerProfile.objects.get_or_create(user=self.request.user)
            vacancy.already_applied = Application.objects.filter(vacancy=vacancy, jobseeker=profile).exists()

        context['applications_count'] = vacancy.applications.count()
        return context


class CompanyUpdateView(LoginRequiredMixin, UpdateView):
    model = Company
    fields = ['name', 'description', 'logo', 'website', 'address', 'founded_year', 'employees_count']
    template_name = 'employers/company_form.html'
    success_url = reverse_lazy('employers:employer_cabinet')

    def get_object(self, queryset=None):
        # Автоматически создаём компанию, если её нет
        company, created = Company.objects.get_or_create(
            user=self.request.user,
            defaults={'name': f"Компания {self.request.user.username}"}
        )
        if created:
            messages.success(self.request, "Профиль компании создан! Заполните данные.")
        return company

class AllVacanciesView(ListView):
    template_name = 'employers/all_vacancies.html'
    context_object_name = 'vacancies'
    paginate_by = 12

    def get_queryset(self):
        qs = Vacancy.objects.filter(is_active=True).select_related('company', 'category')

        # === ФИЛЬТРЫ ===
        q = self.request.GET.get('q')
        category = self.request.GET.get('category')
        salary_from = self.request.GET.get('salary_from')
        duties = self.request.GET.get('duties')

        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(company__name__icontains=q) | Q(description__icontains=q))
        if category:
            qs = qs.filter(category_id=category)
        if salary_from:
            qs = qs.filter(salary_from__gte=salary_from)
        if duties:
            qs = qs.filter(responsibilities__icontains=duties)

        # === ДОБАВЛЯЕМ already_applied ДЛЯ ВСЕХ ВАКАНСИЙ ===
        if self.request.user.is_authenticated and self.request.user.role == 'jobseeker':
            profile, _ = JobseekerProfile.objects.get_or_create(user=self.request.user)
            applied_ids = set(Application.objects.filter(jobseeker=profile).values_list('vacancy_id', flat=True))

            for vacancy in qs:
                vacancy.already_applied = vacancy.pk in applied_ids
        else:
            for vacancy in qs:
                vacancy.already_applied = False

        return qs.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()

        # ← ЭТА СТРОКА РЕШАЕТ ВСЁ
        if self.request.user.is_authenticated and self.request.user.role == 'jobseeker':
            profile, _ = JobseekerProfile.objects.get_or_create(user=self.request.user)
            applied_ids = Application.objects.filter(jobseeker=profile).values_list('vacancy_id', flat=True)
            context['applied_vacancy_ids'] = list(applied_ids)
        else:
            context['applied_vacancy_ids'] = []

        return context


class AllCompaniesView(ListView):
    template_name = 'employers/all_companies.html'
    context_object_name = 'companies'
    paginate_by = 15

    def get_queryset(self):
        qs = Company.objects.annotate(
            active_vacancies_count=Count('vacancies', filter=Q(vacancies__is_active=True))
        )

        # Поиск по названию
        search = self.request.GET.get('search')
        if search:
            qs = qs.filter(name__icontains=search)

        # Показываем только компании, у которых есть хотя бы одна активная вакансия
        return qs.filter(active_vacancies_count__gt=0).order_by('-active_vacancies_count')

class VacancyCreateView(LoginRequiredMixin, CreateView):
    model = Vacancy
    form_class = VacancyForm  # ← теперь используем форму
    template_name = 'employers/vacancy_form.html'

    def form_valid(self, form):
        form.instance.company = self.request.user.company
        messages.success(self.request, f"Вакансия «{form.instance.title}» успешно создана!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('employers:employer_cabinet')


class VacancyUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Vacancy
    form_class = VacancyForm  # ← используем ту же форму
    template_name = 'employers/vacancy_form.html'

    def test_func(self):
        return self.get_object().company == self.request.user.company

    def get_success_url(self):
        messages.success(self.request, "Вакансия успешно обновлена!")
        return reverse_lazy('employers:vacancy_detail', kwargs={'pk': self.object.pk})


class VacancyDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Мгновенное удаление вакансии без отдельного шаблона подтверждения.
    Работает по GET-запросу с JavaScript confirm().
    """
    def test_func(self):
        self.vacancy = Vacancy.objects.get(pk=self.kwargs['pk'])
        return (self.vacancy.company.user == self.request.user or
                self.request.user.is_staff)

    def get(self, request, *args, **kwargs):
        if not self.test_func():
            messages.error(request, "У вас нет прав на удаление этой вакансии.")
            return HttpResponseRedirect(reverse_lazy('employers:employer_cabinet'))

        title = self.vacancy.title
        self.vacancy.delete()
        messages.warning(request, f'Вакансия «{title}» успешно удалена.')
        return HttpResponseRedirect(reverse_lazy('employers:employer_cabinet'))


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


@login_required
def update_application_status(request, application_id):
    if request.method != "POST":
        return redirect('employers:applications')

    application = get_object_or_404(Application, id=application_id)

    # Проверка прав
    if application.vacancy.company.user != request.user:
        messages.error(request, "Доступ запрещён")
        return redirect('employers:applications')

    new_status = request.POST.get("status")

    # ← ИСПРАВЛЕНО: берём choices напрямую из поля модели!
    valid_statuses = [choice[0] for choice in Application.status.field.choices]

    if new_status in valid_statuses:
        old_status = application.get_status_display()
        application.status = new_status
        application.save()

        # Уведомление соискателю
        try:
            Notification.objects.create(
                user=application.jobseeker.user,
                title="Статус отклика изменён",
                message=f'Вакансия «{application.vacancy.title}»: {old_status} → {application.get_status_display()}',
                url=reverse('jobseekers:my_applications')
            )
        except:
            pass

        messages.success(request, f"Статус изменён на «{application.get_status_display()}»")
    else:
        messages.error(request, "Неверный статус")

    return redirect('employers:applications')


# employers/views.py — замени функцию полностью
# employers/views.py
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse


@login_required
def invite_jobseeker(request, username):
    if request.user.role != 'employer' or not request.user.company:
        messages.error(request, "Только работодатели могут приглашать")
        return redirect('jobseekers:resume_list')

    profile = get_object_or_404(JobseekerProfile, user__username=username)
    company = request.user.company
    active_vacancies = Vacancy.objects.filter(company=company, is_active=True)

    if not active_vacancies.exists():
        messages.warning(request, "У вас нет активных вакансий")
        return redirect(request.META.get('HTTP_REFERER') or 'jobseekers:resume_list')

    if request.method == "POST":
        vacancy_id = request.POST.get("vacancy")
        vacancy = get_object_or_404(Vacancy, id=vacancy_id, company=company)

        app, created = Application.objects.get_or_create(
            jobseeker=profile,
            vacancy=vacancy,
            defaults={
                'status': 'interview',
                'cover_letter': f"Приглашение от компании {company.name}"
            }
        )

        if created:
            # ← ИСПРАВЛЕНО: убрал url, если его нет в модели
            Notification.objects.create(
                user=profile.user,
                title="Вас пригласили на вакансию!",
                message=f'Компания «{company.name}» приглашает на «{vacancy.title}»'
                # url=reverse('jobseekers:my_applications')  ← УБРАЛ ЭТУ СТРОКУ!
            )
            messages.success(request, f"Приглашение отправлено на «{vacancy.title}»")
        else:
            messages.info(request, "Это приглашение уже было отправлено")

        return redirect(request.META.get('HTTP_REFERER') or 'jobseekers:resume_list')

    return render(request, 'employers/invite_form.html', {
        'jobseeker': profile,
        'vacancies': active_vacancies,
    })