from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, TemplateView
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.db.models import Q

from core_models.models import User, Notification
from .models import Message


class InboxView(LoginRequiredMixin, ListView):
    template_name = 'messenger/inbox.html'
    context_object_name = 'conversations'

    def get_queryset(self):
        user = self.request.user
        # Получаем уникальных собеседников с последним сообщением
        sent = Message.objects.filter(sender=user).values('recipient').annotate(last=Max('sent_at'))
        received = Message.objects.filter(recipient=user).values('sender').annotate(last=Max('sent_at'))

        companion_ids = set(sent.values_list('recipient', flat=True)) | set(received.values_list('sender', flat=True))
        companions = User.objects.filter(id__in=companion_ids).exclude(id=user.id)

        result = []
        for companion in companions:
            last_msg = Message.objects.filter(
                (Q(sender=user) & Q(recipient=companion)) |
                (Q(sender=companion) & Q(recipient=user))
            ).order_by('-sent_at').first()
            unread = Message.objects.filter(sender=companion, recipient=user, is_read=False).count()
            result.append({
                'companion': companion,
                'last_message': last_msg,
                'unread_count': unread
            })
        return result


class DialogView(LoginRequiredMixin, TemplateView):
    template_name = 'messenger/dialog.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        companion = get_object_or_404(User, id=self.kwargs['companion_id'])
        context['companion'] = companion

        messages = Message.objects.filter(
            (Q(sender=self.request.user) & Q(recipient=companion)) |
            (Q(sender=companion) & Q(recipient=self.request.user))
        ).order_by('sent_at')

        # Помечаем как прочитанные
        Message.objects.filter(sender=companion, recipient=self.request.user, is_read=False).update(is_read=True)

        context['messages'] = messages
        return context


def htmx_send_message(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)

    recipient_id = request.POST.get('recipient_id')
    content = request.POST.get('content', '').strip()

    if not content:
        return JsonResponse({'error': 'Сообщение пустое'}, status=400)

    recipient = get_object_or_404(User, id=recipient_id)
    message = Message.objects.create(
        sender=request.user,
        recipient=recipient,
        content=content
    )

    # Уведомление
    Notification.objects.create(
        user=recipient,
        title="Новое сообщение",
        message=f"{request.user.get_full_name() or request.user.username}: {content[:50]}..."
    )

    return render(request, 'messenger/partials/message_bubble.html', {
        'message': message,
        'is_own': True
    })


class NotificationsView(LoginRequiredMixin, ListView):
    template_name = 'messenger/notifications.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        return self.request.user.notifications.order_by('-created_at')


def htmx_mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'success': True})


def htmx_unread_count(request):
    count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({'count': count})