from django.contrib.auth import get_user_model
from django.db import models

from core.models import TimeStampedModel


class Profile(TimeStampedModel):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name="profile")
    timezone = models.CharField(max_length=64, default="UTC")
    email_notifications = models.BooleanField(default=True)
    telegram_chat_id = models.CharField(max_length=128, blank=True)

    def __str__(self) -> str:
        return f"Profile<{self.user.username}>"
