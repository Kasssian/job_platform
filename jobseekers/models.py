from django.db import models

from core_models.models import User, Skill, Category
from phonenumber_field.modelfields import PhoneNumberField

class JobseekerProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='jobseeker_profile',
        limit_choices_to={'role': 'jobseeker'},
        verbose_name='Соискатель'
    )
    about = models.TextField(blank=True, verbose_name='О себе')
    desired_position = models.CharField(max_length=200, verbose_name='Желаемая должность')
    desired_salary_from = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True,
                                              verbose_name='Зарплата от')
    desired_salary_to = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True,
                                            verbose_name='Зарплата до')
    experience_years = models.PositiveSmallIntegerField(default=0, verbose_name='Опыт работы, лет')
    phone_number = PhoneNumberField(region='KG')
    is_open_to_work = models.BooleanField(default=True, verbose_name='Ищу работу')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлён')

    class Meta:
        verbose_name = 'Резюме соискателя'
        verbose_name_plural = 'Резюме соискателей'

    def __str__(self):
        return f'{self.user.get_full_name() or self.user.username} — {self.desired_position}'


class Education(models.Model):
    profile = models.ForeignKey(JobseekerProfile, on_delete=models.CASCADE, related_name='education')
    institution = models.CharField(max_length=200, verbose_name='Учебное заведение')
    faculty = models.CharField(max_length=200, blank=True, verbose_name='Факультет')
    specialty = models.CharField(max_length=200, verbose_name='Специальность')
    degree = models.CharField(max_length=100, choices=[
        ('secondary', 'Среднее'), ('vocational', 'СПО'), ('bachelor', 'Бакалавр'),
        ('master', 'Магистр'), ('phd', 'Кандидат/доктор наук')
    ], verbose_name='Степень')
    start_year = models.PositiveSmallIntegerField()
    end_year = models.PositiveSmallIntegerField(blank=True, null=True)
    is_current = models.BooleanField(default=False, verbose_name='Учусь сейчас')

    class Meta:
        ordering = ['-end_year', '-start_year']
        verbose_name = 'Образование'
        verbose_name_plural = 'Образование'


class Experience(models.Model):
    profile = models.ForeignKey(JobseekerProfile, on_delete=models.CASCADE, related_name='experience')
    company = models.CharField(max_length=200, verbose_name='Компания')
    position = models.CharField(max_length=200, verbose_name='Должность')
    description = models.TextField(blank=True, verbose_name='Обязанности и достижения')
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False, verbose_name='Работаю сейчас')

    class Meta:
        ordering = ['-is_current', '-start_date']
        verbose_name = 'Опыт работы'
        verbose_name_plural = 'Опыт работы'


class JobseekerSkill(models.Model):
    profile = models.ForeignKey(JobseekerProfile, on_delete=models.CASCADE, related_name='skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    level = models.PositiveSmallIntegerField(
        choices=[(1, 'Начальный'), (2, 'Средний'), (3, 'Продвинутый'), (4, 'Эксперт')],
        default=2)

    class Meta:
        unique_together = ('profile', 'skill')
        verbose_name = 'Навык соискателя'
        verbose_name_plural = 'Навыки соискателей'
