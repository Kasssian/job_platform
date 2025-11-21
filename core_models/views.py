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

from .forms import CustomUserCreationForm
from .models import Category
from .models import Skill, Notification, Review
from .serializers import CategorySerializer, SkillSerializer, NotificationSerializer, ReviewSerializer


class CustomLoginView(LoginView):
    template_name = 'core_models/login.html'
    redirect_authenticated_user = True


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
            return redirect('jobseekers:profile')
        elif self.object.role == 'employer':
            return redirect('employes:company_profile')
        return response


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core_models/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.role == 'jobseeker' and hasattr(user, 'jobseeker_profile'):
            context['profile'] = user.jobseeker_profile
            context['role_name'] = 'Соискатель'
        elif user.role == 'employer' and hasattr(user, 'company'):
            context['profile'] = user.company
            context['role_name'] = 'Работодатель'
        else:
            context['role_name'] = 'Не выбран'

        context['unread_notifications'] = user.notifications.filter(is_read=False).count()
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
