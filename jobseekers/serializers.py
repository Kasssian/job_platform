from rest_framework import serializers
from core_models.serializers import SkillSerializer
from .models import JobseekerProfile, Education, Experience, JobseekerSkill, Skill


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = ['id', 'institution', 'faculty', 'specialty', 'degree', 'start_year', 'end_year', 'is_current']


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = ['id', 'company', 'position', 'description', 'start_date', 'end_date', 'is_current']


class JobseekerSkillSerializer(serializers.ModelSerializer):
    skill = SkillSerializer(read_only=True)
    skill_id = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.all(), source='skill', write_only=True
    )

    class Meta:
        model = JobseekerSkill
        fields = ['skill', 'skill_id', 'level']


class JobseekerProfileListSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.get_full_name', default='Пользователь')
    skills = JobseekerSkillSerializer(source='skills', many=True, read_only=True)

    class Meta:
        model = JobseekerProfile
        fields = [
            'id', 'user', 'desired_position', 'desired_salary_from',
            'desired_salary_to', 'experience_years', 'is_open_to_work',
            'skills', 'updated_at'
        ]


class JobseekerProfileDetailSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.get_full_name')
    education = EducationSerializer(many=True, read_only=True)
    experience = ExperienceSerializer(many=True, read_only=True)
    skills = JobseekerSkillSerializer(source='skills', many=True, read_only=True)

    class Meta:
        model = JobseekerProfile
        fields = '__all__'
        read_only_fields = ['user', 'updated_at']


class JobseekerProfileUpdateSerializer(serializers.ModelSerializer):
    skills = JobseekerSkillSerializer(many=True, required=False)

    class Meta:
        model = JobseekerProfile
        fields = [
            'about', 'desired_position', 'desired_salary_from',
            'desired_salary_to', 'experience_years', 'is_open_to_work', 'skills'
        ]

    def update(self, instance, validated_data):
        skills_data = validated_data.pop('skills', None)

        instance = super().update(instance, validated_data)

        if skills_data is not None:
            instance.skills.all().delete()
            for item in skills_data:
                JobseekerSkill.objects.create(profile=instance, **item)

        return instance