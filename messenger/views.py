from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, TemplateView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from core_models.models import User, Notification
from .models import Message
from .serializers import MessageSerializer


class InboxView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'messenger/inbox.html'
    context_object_name = 'messages'

    def get_queryset(self):
        return Message.objects.filter(recipient=self.request.user).order_by('-created_at')


class DialogView(LoginRequiredMixin, TemplateView):
    template_name = 'messenger/dialog.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        companion_id = self.kwargs['user_id']
        companion = get_object_or_404(User, id=companion_id)
        context['companion'] = companion
        context['dialog'] = Message.objects.filter(
            (Q(sender=self.request.user) & Q(recipient=companion)) |
            (Q(sender=companion) & Q(recipient=self.request.user))
        ).order_by('created_at')
        return context


class NotificationsView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'messenger/notifications.html'
    context_object_name = 'notifications'

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')


# HTMX: Отправка сообщения в мессенджере, здесь надо аккуратнее с POST-запросом.
def htmx_send_message(request):
    if request.method == 'POST':
        recipient_id = request.POST.get('recipient_id')
        content = request.POST.get('content', '').strip()
        recipient = get_object_or_404(User, id=recipient_id)

        if not content:
            return JsonResponse({'error': 'Сообщение не может быть пустым'}, status=400)

        message = Message.objects.create(
            sender=request.user,
            recipient=recipient,
            content=content
        )
        Notification.objects.create(
            user=recipient,
            title='Новое сообщение',
            message=f'Новое сообщение от {request.user.get_full_name()}'
        )
        return render(request, 'messenger/partials/message_item.html', {'message': message})

    return JsonResponse({'error': 'Недопустимый запрос'}, status=400)


# HTMX: Пометить уведомление как прочитанное, типа уведомления гаснут при просмотре, как в Ютубе.
def htmx_mark_notification_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'status': 'ok'})


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Message.objects.filter(
            Q(sender=self.request.user) | Q(recipient=self.request.user)
        ).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)
