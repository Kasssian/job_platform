from django.db import models

from core_models.models import User


class ChatRoom(models.Model):
    participant1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_rooms_p1')
    participant2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_rooms_p2')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('participant1', 'participant2')

    def __str__(self):
        return f'Чат {self.participant1} и {self.participant2}'

    @classmethod
    def get_or_create_room(cls, user1, user2):
        if user1.id > user2.id:
            user1, user2 = user2, user1
        room, _ = cls.objects.get_or_create(participant1=user1, participant2=user2)
        return room


class Message(models.Model):
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', verbose_name='Отправитель')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages',
                                  verbose_name='Получатель')
    subject = models.CharField(max_length=255, verbose_name='Тема')
    body = models.TextField(verbose_name='Сообщение')
    is_read = models.BooleanField(default=False, verbose_name='Прочитано')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Отправлено')

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['-sent_at']

    def __str__(self):
        return f'{self.sender} отправлен {self.recipient}: {self.subject}'
