from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/create/', views.ProfileCreateView.as_view(), name='profile_create'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
]