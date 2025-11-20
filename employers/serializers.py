# employers/serializers.py
from rest_framework import serializers

from core_models.models import Skill
from core_models.serializers import CategorySerializer, SkillSerializer
from .models import Company, Vacancy, Application


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'description', 'logo', 'website',
            'address', 'founded_year', 'employees_count'
        ]


class VacancyListSerializer(serializers.ModelSerializer):
    company = serializers.CharField(source='company.name')
    category = CategorySerializer()
    skills = SkillSerializer(many=True)

    class Meta:
        model = Vacancy
        fields = [
            'id', 'title', 'company', 'category', 'location',
            'salary_from', 'salary_to', 'is_active', 'created_at', 'skills'
        ]


class VacancyDetailSerializer(serializers.ModelSerializer):
    company = CompanySerializer()
    category = CategorySerializer()
    skills = SkillSerializer(many=True)

    class Meta:
        model = Vacancy
        fields = '__all__'


class VacancyCreateUpdateSerializer(serializers.ModelSerializer):
    skills = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.all(), many=True, required=False
    )

    class Meta:
        model = Vacancy
        fields = [
            'title', 'description', 'requirements', 'responsibilities',
            'salary_from', 'salary_to', 'location', 'category', 'skills', 'is_active'
        ]

    def create(self, validated_data):
        skills = validated_data.pop('skills', [])
        vacancy = super().create(validated_data)
        vacancy.skills.set(skills)
        return vacancy

    def update(self, instance, validated_data):
        skills = validated_data.pop('skills', None)
        instance = super().update(instance, validated_data)
        if skills is not None:
            instance.skills.set(skills)
        return instance


class ApplicationSerializer(serializers.ModelSerializer):
    jobseeker = serializers.StringRelatedField()
    vacancy = serializers.StringRelatedField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Application
        fields = ['id', 'jobseeker', 'vacancy', 'cover_letter', 'status', 'status_display', 'applied_at']
        read_only_fields = ['jobseeker', 'applied_at']