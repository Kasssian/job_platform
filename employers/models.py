from django.db import models

from core_models.models import User, Category, Skill


class Company(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company',
                                limit_choices_to={'role': 'employer'}, verbose_name='Работодатель')
    name = models.CharField(max_length=200, verbose_name='Название компании')
    description = models.TextField(blank=True, verbose_name='Описание')
    logo = models.ImageField(upload_to='company_logos/', blank=True, verbose_name='Логотип')
    website = models.URLField(blank=True, verbose_name='Сайт')
    address = models.CharField(max_length=255, blank=True, verbose_name='Адрес')

    class Meta:
        verbose_name = 'Компания'
        verbose_name_plural = 'Компании'

    def __str__(self):
        return self.name


class Vacancy(models.Model):
    """Вакансия работодателя."""
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='vacancies',
                                verbose_name='Компания')
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    requirements = models.TextField(verbose_name='Требования')
    salary_from = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True,
                                      verbose_name='Зарплата от')
    salary_to = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True,
                                    verbose_name='Зарплата до')
    location = models.CharField(max_length=100, verbose_name='Локация')
    category = models.ForeignKey('core_models.Category', on_delete=models.SET_NULL, null=True,
                                 verbose_name='Категория')
    skills = models.ManyToManyField('core_models.Skill', related_name='vacancy_skills',
                                    verbose_name='Требуемые навыки')
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')

    class Meta:
        verbose_name = 'Вакансия'
        verbose_name_plural = 'Вакансии'

    def __str__(self):
        return f'{self.title} — {self.company.name}'
