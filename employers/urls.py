from django.urls import path
from . import views

app_name = 'jobseekers'

urlpatterns = [
    # Профиль соискателя
    path('profile/', views.JobseekerProfileView.as_view(), name='profile'),
    path('profile/edit/', views.JobseekerProfileUpdateView.as_view(), name='profile_edit'),

    # Образование и опыт
    path('education/add/', views.EducationCreateView.as_view(), name='education_add'),
    path('experience/add/', views.ExperienceCreateView.as_view(), name='experience_add'),

    # Личный кабинет
    path('cabinet/', views.JobseekerCabinetView.as_view(), name='cabinet'),
    path('applications/', views.MyApplicationsView.as_view(), name='my_applications'),

    # HTMX действия
    path('htmx/add-skill/', views.htmx_add_skill, name='htmx_add_skill'),
    path('htmx/apply/<int:vacancy_id>/', views.htmx_apply_vacancy, name='htmx_apply_vacancy'),
]