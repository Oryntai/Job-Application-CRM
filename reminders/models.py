from django.db import models
from django.utils import timezone

from applications.models import JobApplication
from core.models import OwnedModel, TimeStampedModel


class ReminderChannel(models.TextChoices):
    EMAIL = "EMAIL", "Email"
    TELEGRAM = "TELEGRAM", "Telegram"


class ReminderStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    SENT = "SENT", "Sent"
    FAILED = "FAILED", "Failed"
    CANCELLED = "CANCELLED", "Cancelled"


class Reminder(OwnedModel, TimeStampedModel):
    application = models.ForeignKey(
        JobApplication, on_delete=models.CASCADE, related_name="reminders"
    )
    remind_at = models.DateTimeField()
    channel = models.CharField(
        max_length=10, choices=ReminderChannel.choices, default=ReminderChannel.EMAIL
    )
    message = models.CharField(max_length=500)
    status = models.CharField(
        max_length=10, choices=ReminderStatus.choices, default=ReminderStatus.PENDING
    )

    class Meta:
        ordering = ["remind_at", "id"]

    @property
    def is_overdue(self) -> bool:
        return self.status == ReminderStatus.PENDING and self.remind_at < timezone.now()


class NotificationLog(TimeStampedModel):
    reminder = models.ForeignKey(Reminder, on_delete=models.CASCADE, related_name="logs")
    sent_at = models.DateTimeField(default=timezone.now)
    provider_response = models.JSONField(default=dict, blank=True)
    success = models.BooleanField(default=False)

    class Meta:
        ordering = ["-sent_at", "-id"]
