from django.contrib import admin
from .models import ChatRoom, Message


@admin.register(ChatRoom)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'vacancy', 'jobseeker', 'employer', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('vacancy__title', 'jobseeker__user__username', 'employer__username')
    raw_id_fields = ('vacancy', 'jobseeker', 'employer')
    readonly_fields = ('created_at',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('chat', 'sender', 'text_preview', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('sender__username', 'text')
    raw_id_fields = ('chat', 'sender')
    readonly_fields = ('created_at',)

    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Текст'