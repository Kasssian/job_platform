# employers/urls.py

from django.urls import path
from . import views
from .views import VacancyDeleteView  # оставляем, если используешь

app_name = 'employers'

urlpatterns = [
    # ────── ПУБЛИЧНЫЕ СТРАНИЦЫ (доступны всем) ──────
    path('vacancies/', views.AllVacanciesView.as_view(), name='all_vacancies'),  # ← Все вакансии + фильтры
    path('companies/', views.AllCompaniesView.as_view(), name='all_companies'),  # ← Все компании + поиск

    # ────── ДЕТАЛЬНЫЕ СТРАНИЦЫ ──────
    path('vacancy/<int:pk>/', views.VacancyDetailView.as_view(), name='vacancy_detail'),
    path('company/<int:company_id>/', views.CompanyProfileView.as_view(), name='company_profile'),

    # ────── ДЛЯ РАБОТОДАТЕЛЕЙ (личный кабинет) ──────
    path('cabinet/', views.EmployerCabinetView.as_view(), name='employer_cabinet'),
    path('company/edit/', views.CompanyUpdateView.as_view(), name='company_edit'),

    # Управление вакансиями
    path('vacancy/create/', views.VacancyCreateView.as_view(), name='vacancy_create'),
    path('vacancy/<int:pk>/edit/', views.VacancyUpdateView.as_view(), name='vacancy_edit'),
    path('vacancy/<int:pk>/delete/', VacancyDeleteView.as_view(), name='vacancy_delete'),  # или views.VacancyDeleteView

    # Отклики
    path('applications/', views.VacancyApplicationsView.as_view(), name='applications'),
    path('applications/vacancy/<int:vacancy_id>/', views.VacancyApplicationsView.as_view(),
         name='applications_by_vacancy'),

    path('applications/update/<int:application_id>/',
         views.update_application_status,
         name='update_application_status'),
    path('invite/<str:username>/', views.invite_jobseeker, name='invite_jobseeker'),
]
