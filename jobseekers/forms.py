# jobseekers/forms.py
from django import forms
from .models import JobseekerProfile, Education, Experience

class JobseekerProfileForm(forms.ModelForm):
    class Meta:
        model = JobseekerProfile
        fields = [
            'desired_position', 'desired_salary_from', 'desired_salary_to',
            'about', 'experience_years', 'phone_number', 'is_open_to_work'
        ]
        widgets = {
            'about': forms.Textarea(attrs={'rows': 5}),
        }

class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = '__all__'
        exclude = ['profile']

class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = '__all__'
        exclude = ['profile']