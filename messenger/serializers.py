from rest_framework import serializers
from django.contrib.auth import get_user_model
from jobseekers.serializers import ResumeListSerializer
from employers.serializers import VacancyListSerializer
from .models import Response, Message, Notification, Review

User = get_user_model()


class ResponseSerializer(serializers.ModelSerializer):
    resume = ResumeListSerializer(read_only=True)
    vacancy = VacancyListSerializer(read_only=True)
    applicant = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Response
        fields = ['id', 'vacancy', 'resume', 'applicant', 'cover_letter', 'status', 'created_at']
        read_only_fields = ['applicant', 'status', 'created_at']


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