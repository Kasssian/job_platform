from django.contrib.auth import get_user_model
from rest_framework import serializers

from core_models.models import Notification, Review
from jobseekers.models import JobseekerProfile
from .models import Message

User = get_user_model()


class ResumeInChatSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    avatar = serializers.ImageField(source='user.avatar', read_only=True)
    desired_position = serializers.CharField()
    experience_years = serializers.IntegerField()
    skills = serializers.SerializerMethodField()

    class Meta:
        model = JobseekerProfile
        fields = ['id', 'full_name', 'avatar', 'desired_position', 'experience_years', 'skills', 'desired_salary_from',
                  'desired_salary_to']

    def get_skills(self, obj):
        return [
            {"name": js.skill.name, "level": js.level, "level_display": js.get_level_display()}
            for js in obj.skills.select_related('skill').all()[:10]]


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField(read_only=True)
    receiver = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'is_read', 'created_at']
        read_only_fields = ['sender', 'is_read', 'created_at']


class NotificationSerializer(serializers.ModelSerializer):
    actor = serializers.StringRelatedField()
    target_url = serializers.CharField(read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'content', 'actor', 'target_url', 'is_read', 'created_at']
        read_only_fields = ['actor', 'target_url', 'created_at']


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    target = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'author', 'target', 'rating', 'comment', 'created_at']
        read_only_fields = ['author', 'created_at']
