from django import forms
from core_models.models import Skill
from .models import Vacancy

class VacancyForm(forms.ModelForm):
    skills = forms.ModelMultipleChoiceField(
        queryset=Skill.objects.all().order_by('name'),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Требуемые навыки"
    )

    class Meta:
        model = Vacancy
        fields = [
            'title', 'category', 'location',
            'salary_from', 'salary_to',
            'description', 'requirements', 'responsibilities',
            'skills', 'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6}),
            'requirements': forms.Textarea(attrs={'rows': 5}),
            'responsibilities': forms.Textarea(attrs={'rows': 5}),
        }