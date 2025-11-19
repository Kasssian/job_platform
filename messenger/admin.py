from django.contrib import admin

from .models import ChatRoom, Message


@admin.register(ChatRoom)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'vacancy', 'job_seeker', 'employer', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('vacancy__title', 'job_seeker__email', 'employer__user__email')
    readonly_fields = ('created_at',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('chat', 'sender', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('text', 'sender__email')
    readonly_fields = ('created_at',)
