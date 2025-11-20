from django.contrib.auth import get_user_model
from rest_framework import serializers

from core_models.models import Skill
from core_models.serializers import SkillSerializer, CategorySerializer
from .models import JobseekerProfile, Education, Experience

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
        model = JobseekerProfile
        fields = [
            'id', 'user', 'phone', 'birth_date',
            'about', 'avatar', 'skills', 'skill_ids', 'is_premium',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


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
