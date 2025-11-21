from django.contrib import admin

from .models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'content_preview', 'sent_at', 'is_read')
    list_filter = ('is_read', 'sent_at')
    search_fields = ('sender__username', 'recipient__username', 'content')
    readonly_fields = ('sender', 'recipient', 'sent_at', 'is_read')

    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    content_preview.short_description = 'Сообщение'
