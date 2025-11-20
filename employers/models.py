from django.db import models

from core_models.models import User, Category
from jobseekers.models import JobseekerProfile


class Company(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='company',
        limit_choices_to={'role': 'employer'},
        verbose_name='Работодатель'
    )
    name = models.CharField(max_length=200, verbose_name='Название компании')
    description = models.TextField(blank=True, verbose_name='О компании')
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True, verbose_name='Логотип')
    website = models.URLField(blank=True, verbose_name='Сайт')
    address = models.CharField(max_length=255, blank=True, verbose_name='Адрес')
    founded_year = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Год основания')
    employees_count = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Количество сотрудников')

    class Meta:
        verbose_name = 'Компания'
        verbose_name_plural = 'Компании'

    def __str__(self):
        return self.name


class Vacancy(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='vacancies',
                                verbose_name='Компания')
    title = models.CharField(max_length=200, verbose_name='Должность')
    description = models.TextField(verbose_name='Описание вакансии')
    requirements = models.TextField(verbose_name='Требования')
    responsibilities = models.TextField(blank=True, verbose_name='Обязанности')
    salary_from = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    salary_to = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    location = models.CharField(max_length=100, verbose_name='Город')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name='Категория')
    skills = models.ManyToManyField('core_models.Skill', related_name='required_in_vacancies')
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Вакансия'
        verbose_name_plural = 'Вакансии'
        ordering = ['-created_at']


class Application(models.Model):
    jobseeker = models.ForeignKey(JobseekerProfile, on_delete=models.CASCADE, related_name='applications',
                                  verbose_name='Соискатель')
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name='applications',
                                verbose_name='Вакансия')
    cover_letter = models.TextField(blank=True, verbose_name='Сопроводительное письмо')
    status = models.CharField(max_length=20, choices=[
        ('sent', 'Отправлено'),
        ('viewed', 'Просмотрено'),
        ('interview', 'Приглашён'),
        ('rejected', 'Отказано'),
        ('hired', 'Принят'),
    ], default='sent')
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('jobseeker', 'vacancy')
        verbose_name = 'Отклик'
        verbose_name_plural = 'Отклики'
