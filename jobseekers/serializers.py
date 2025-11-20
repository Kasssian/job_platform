from django.contrib.auth import get_user_model
from rest_framework import serializers

from core_models.models import Skill
from core_models.serializers import SkillSerializer, CategorySerializer
from .models import Profile, Resume, Education, Experience

User = get_user_model()


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = ['id', 'institution', 'faculty', 'specialty', 'start_year', 'end_year', 'is_current']


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = ['id', 'company', 'position', 'start_date', 'end_date', 'is_current', 'description']


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    skill_ids = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.all(), many=True, write_only=True, source='skills'
    )

    class Meta:
        model = Profile
        fields = [
            'id', 'user', 'phone', 'birth_date',
            'about', 'avatar', 'skills', 'skill_ids', 'is_premium',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


class ResumeListSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()
    category = CategorySerializer()
    skills = SkillSerializer(many=True)

    class Meta:
        model = Resume
        fields = ['id', 'title', 'author', 'category', 'desired_salary_max', 'experience_years', 'is_active', 'skills',
                  'created_at']


class ResumeDetailSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()
    category = CategorySerializer()
    skills = SkillSerializer(many=True)
    education = EducationSerializer(many=True)
    experience = ExperienceSerializer(many=True)

    class Meta:
        model = Resume
        fields = '__all__'


class ResumeCreateUpdateSerializer(serializers.ModelSerializer):
    skill_ids = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.all(), many=True, write_only=True, source='skills'
    )
    education = EducationSerializer(many=True, required=False)
    experience = ExperienceSerializer(many=True, required=False)

    class Meta:
        model = Resume
        fields = ['title', 'category', 'description', 'desired_salary', 'experience_years',
                  'skill_ids', 'education', 'experience', 'is_active']

    def create(self, validated_data):
        skills = validated_data.pop('skills', [])
        education_data = validated_data.pop('education', [])
        experience_data = validated_data.pop('experience', [])

        resume = Resume.objects.create(author=self.context['request'].user, **validated_data)
        resume.skills.set(skills)

        for edu in education_data:
            Education.objects.create(resume=resume, **edu)
        for exp in experience_data:
            Experience.objects.create(resume=resume, **exp)

        return resume

    def update(self, instance, validated_data):
        skills = validated_data.pop('skills', None)
        education_data = validated_data.pop('education', None)
        experience_data = validated_data.pop('experience', None)

        instance = super().update(instance, validated_data)

        if skills is not None:
            instance.skills.set(skills)
        if education_data is not None:
            instance.education.all().delete()
            for edu in education_data:
                Education.objects.create(resume=instance, **edu)
        if experience_data is not None:
            instance.experience.all().delete()
            for exp in experience_data:
                Experience.objects.create(resume=instance, **exp)

        return instance
