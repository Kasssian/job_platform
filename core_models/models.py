""" Главные модели сайта. Не трогать ёптм! """

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    JOB_SEEKER = 'job_seeker'
    EMPLOYER = 'employer'
    ADMIN = 'admin'
    ROLE_CHOICES = [
        (JOB_SEEKER, _('Соискатель')),
        (EMPLOYER, _('Работодатель')),
        (ADMIN, _('Администратор')),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=JOB_SEEKER)
    phone = models.CharField(max_length=20, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def is_job_seeker(self):
        return self.role == self.JOB_SEEKER

    def is_employer(self):
        return self.role == self.EMPLOYER


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Skill(models.Model):
    """Навыки (общие для резюме и вакансий)."""
    name = models.CharField(max_length=100, unique=True, verbose_name='Навык')

    class Meta:
        verbose_name = 'Навык'
        verbose_name_plural = 'Навыки'

    def __str__(self):
        return self.name


class Notification(models.Model):
    """Уведомления для пользователей."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications',
                             verbose_name='Пользователь')
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    message = models.TextField(verbose_name='Сообщение')
    is_read = models.BooleanField(default=False, verbose_name='Прочитано')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        ordering = ['-created_at']


class Review(models.Model):
    """Отзывы / рейтинги между пользователями."""
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews',
                                 verbose_name='Оставил отзыв')
    reviewed = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_reviews',
                                 verbose_name='Получил отзыв')
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)], verbose_name='Рейтинг')
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        unique_together = ('reviewer', 'reviewed')
