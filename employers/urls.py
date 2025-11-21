from django.urls import path
from . import views

app_name = 'employers'

urlpatterns = [
    # Список и поиск вакансий (общий для всех)
    path('vacancies/', views.VacancyListView.as_view(), name='vacancy_list'),
    path('vacancy/<int:pk>/', views.VacancyDetailView.as_view(), name='vacancy_detail'),

    # Профиль компании
    path('company/', views.CompanyProfileView.as_view(), name='company_profile'),
    path('company/edit/', views.CompanyUpdateView.as_view(), name='company_edit'),

    # Управление вакансиями (только для работодателя)
    path('vacancy/create/', views.VacancyCreateView.as_view(), name='vacancy_create'),
    path('vacancy/<int:pk>/edit/', views.VacancyUpdateView.as_view(), name='vacancy_edit'),
    path('vacancy/<int:pk>/delete/', views.VacancyDeleteView.as_view(), name='vacancy_delete'),

    # Личный кабинет работодателя
    path('cabinet/', views.EmployerCabinetView.as_view(), name='employer_cabinet'),
    path('applications/', views.VacancyApplicationsView.as_view(), name='applications'),
    path('applications/vacancy/<int:vacancy_id>/', views.VacancyApplicationsView.as_view(),
         name='applications_by_vacancy'),

    # HTMX действия
    path('htmx/application/<int:application_id>/status/', views.htmx_update_application_status,
         name='htmx_update_status'),
]