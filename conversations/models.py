from django.db import models
from accounts.models import CustomUser
from services.models import Service


class Conversation(models.Model):
    service = models.ForeignKey(
        Service,
        related_name='conversations',
        on_delete=models.CASCADE
    )
    members = models.ManyToManyField(CustomUser, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-modified_at',)

    def __str__(self):
        return f"{self.service} | {self.modified_at}"


class ConversationMessage(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        related_name='messages',
        on_delete=models.CASCADE
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        CustomUser,
        related_name='created_messages',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Conversation Message'
        verbose_name_plural = 'Conversation Messages'

    def __str__(self):
        return f"{self.conversation} | {self.created_at}"
