from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from employers.models import Application
from jobseekers.models import JobseekerProfile
from .forms import CustomUserCreationForm
from .models import Category
from .models import Skill, Notification, Review
from .serializers import CategorySerializer, SkillSerializer, NotificationSerializer, ReviewSerializer


class CustomLoginView(LoginView):
    template_name = 'core_models/login.html'
    # redirect_authenticated_user = True


class HomeView(TemplateView):
    template_name = 'core_models/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        try:
            from employers.models import Vacancy
            context['recent_vacancies'] = Vacancy.objects.filter(is_active=True)[:8]
        except:
            context['recent_vacancies'] = []
        return context


class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'core_models/register.html'
    success_url = reverse_lazy('core:home')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, 'Регистрация успешна! Заполните профиль.')
        # Перенаправляем в зависимости от роли
        if self.object.role == 'jobseeker':
            JobseekerProfile.objects.get_or_create(
                user=self.object,
                defaults={
                    'desired_position': '',
                    'phone_number': '+996',  # можно оставить пустым, если поле позволяет
                    'is_open_to_work': True,
                }
            )
            messages.info(self.request, 'Ваше резюме создано. Заполните его, чтобы начать поиск работы!')
            return redirect('core:dashboard')
        elif self.object.role == 'employer':
            return redirect('core:dashboard')
        return response


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core_models/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Название роли
        context['role_name'] = dict(user.ROLE_CHOICES).get(user.role, user.role.capitalize())

        # Для соискателя
        if user.role == 'jobseeker':
            try:
                profile = user.jobseeker_profile
                context['profile'] = profile

                # Новые отклики (со статусом 'sent')
                context['new_responses_count'] = Application.objects.filter(
                    jobseeker=profile,
                    status='sent'
                ).count()
            except:
                context['new_responses_count'] = 0

        # Для работодателя
        elif user.role == 'employer':
            if hasattr(user, 'company') and user.company:
                context['new_applications'] = Application.objects.filter(
                    vacancy__company=user.company,
                    status='sent'
                ).count()
            else:
                context['new_applications'] = 0

        return context


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class SkillViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'ok'})


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)
