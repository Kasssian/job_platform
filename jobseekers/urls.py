# jobseekers/urls.py
from django.urls import path
from .views import download_resume_pdf

urlpatterns = [
    path('resume/<int:resume_id>/download-pdf/', download_resume_pdf, name='resume-download-pdf'),
]