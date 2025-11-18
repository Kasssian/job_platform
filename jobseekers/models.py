from django.core.validators import MinValueValidator
from django.db import models

from core_models.models import User, Category, Skill


class Resume(models.Model):
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='resumes',
        limit_choices_to={'role': User.JOB_SEEKER}
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    desired_salary = models.PositiveIntegerField(blank=True, null=True)
    experience_years = models.PositiveSmallIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    skills = models.ManyToManyField(Skill, related_name='jobseeker_resumes', blank=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} — {self.owner}"


class Application(models.Model):
    STATUS_CHOICES = [
        ('pending', 'На рассмотрении'),
        ('accepted', 'Принято'),
        ('rejected', 'Отклонено'),
        ('interview', 'Собеседование'),
    ]

    resume = models.ForeignKey('Resume', on_delete=models.CASCADE, related_name='applications')
    vacancy = models.ForeignKey('employers.Vacancy', on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Отклик'
        verbose_name_plural = 'Отклики'
        unique_together = ('resume', 'vacancy')
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.resume} → {self.vacancy}'


class Profile(models.Model):
    """Основной профиль соискателя — расширяет User"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile',
                                limit_choices_to={'role': 'jobseeker'}, verbose_name='Соискатель')
    about = models.TextField(blank=True, verbose_name='О себе')
    desired_position = models.CharField(max_length=200, blank=True, verbose_name='Желаемая должность')
    desired_salary = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True,
                                         verbose_name='Ожидаемая зарплата')
    location = models.CharField(max_length=100, blank=True, verbose_name='Город/регион')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон (доп.)')
    is_visible = models.BooleanField(default=True, verbose_name='Профиль видим для работодателей')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлён')

    class Meta:
        verbose_name = 'Профиль соискателя'
        verbose_name_plural = 'Профили соискателей'

    def __str__(self):
        return f'Профиль: {self.user.get_full_name() or self.user.username}'


class Education(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='education', verbose_name='Профиль')
    institution = models.CharField(max_length=200, verbose_name='Учебное заведение')
    faculty = models.CharField(max_length=200, blank=True, verbose_name='Факультет')
    specialty = models.CharField(max_length=200, verbose_name='Специальность')
    degree = models.CharField(
        max_length=100,
        choices=[
            ('secondary', 'Среднее'),
            ('vocational', 'Среднее профессиональное'),
            ('bachelor', 'Бакалавр'),
            ('master', 'Магистр'),
            ('phd', 'Кандидат/доктор наук'),
        ],
        verbose_name='Степень'
    )
    start_year = models.PositiveSmallIntegerField(validators=[MinValueValidator(1950)])
    end_year = models.PositiveSmallIntegerField(blank=True, null=True,
                                                help_text='Оставьте пустым, если обучаетесь сейчас')
    is_current = models.BooleanField(default=False, verbose_name='Учусь сейчас')

    class Meta:
        verbose_name = 'Образование'
        verbose_name_plural = 'Образование'
        ordering = ['-end_year', '-start_year']

    def __str__(self):
        return f'{self.degree} — {self.institution}'


class Experience(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='experience',
                                verbose_name='Профиль')
    company = models.CharField(max_length=200, verbose_name='Компания')
    position = models.CharField(max_length=200, verbose_name='Должность')
    description = models.TextField(blank=True, verbose_name='Обязанности и достижения')
    start_date = models.DateField(verbose_name='Дата начала')
    end_date = models.DateField(blank=True, null=True,
                                help_text='Оставьте пустым, если работаете сейчас')
    is_current = models.BooleanField(default=False, verbose_name='Работаю сейчас')

    class Meta:
        verbose_name = 'Опыт работы'
        verbose_name_plural = 'Опыт работы'
        ordering = ['-is_current', '-start_date']

    def __str__(self):
        return f'{self.position} в {self.company}'
