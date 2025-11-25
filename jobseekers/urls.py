# jobseekers/urls.py
from django.urls import path
from . import views

app_name = 'jobseekers'

urlpatterns = [
    path('cabinet/', views.JobseekerCabinetView.as_view(), name='cabinet'),
    path('profile/edit/', views.JobseekerProfileUpdateView.as_view(), name='profile_edit'),

    # Добавление
    path('experience/add/', views.ExperienceCreateView.as_view(), name='experience_add'),
    path('education/add/', views.EducationCreateView.as_view(), name='education_add'),

    # Удаление — как у навыков
    path('remove-experience/<int:experience_id>/', views.remove_experience, name='remove_experience'),
    path('remove-education/<int:education_id>/', views.remove_education, name='remove_education'),

    # Навыки
    path('add-skill/', views.add_skill, name='add_skill'),
    path('remove-skill/<int:skill_id>/', views.remove_skill, name='remove_skill'),

    path('applications/', views.MyApplicationsView.as_view(), name='my_applications'),
    path('resumes/', views.ResumeListView.as_view(), name='resume_list'),
    path('resume/<str:username>/', views.ResumeDetailView.as_view(), name='resume_detail'),
    path('apply-vacancy/<int:pk>/', views.ApplyVacancyView.as_view(), name='apply_vacancy'),
]
