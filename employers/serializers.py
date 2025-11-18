from rest_framework import serializers

from core_models.models import Skill
from core_models.serializers import CategorySerializer, SkillSerializer
from .models import Company, Vacancy


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'description', 'logo', 'website', 'address', 'phone', 'founded_year']


class VacancyListSerializer(serializers.ModelSerializer):
    company = CompanySerializer()
    category = CategorySerializer()

    class Meta:
        model = Vacancy
        fields = ['id', 'title', 'company', 'category', 'city',
                  'is_active', 'created_at']


class VacancyDetailSerializer(serializers.ModelSerializer):
    company = CompanySerializer()
    category = CategorySerializer()
    required_skills = SkillSerializer(many=True)

    class Meta:
        model = Vacancy
        fields = '__all__'


class VacancyCreateUpdateSerializer(serializers.ModelSerializer):
    required_skill_ids = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.all(), many=True, write_only=True, source='required_skills'
    )

    class Meta:
        model = Vacancy
        fields = [
            'title', 'company', 'category', 'description', 'requirements', 'salary_to', 'salary_from', 'skills',
            'required_skill_ids', 'is_active']

    def create(self, validated_data):
        skills = validated_data.pop('required_skills', [])
        vacancy = Vacancy.objects.create(author=self.context['request'].user, **validated_data)
        vacancy.required_skills.set(skills)
        return vacancy

    def update(self, instance, validated_data):
        skills = validated_data.pop('required_skills', None)
        instance = super().update(instance, validated_data)
        if skills is not None:
            instance.required_skills.set(skills)
        return instance
