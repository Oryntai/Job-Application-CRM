from django.utils import timezone

from .models import Reminder, ReminderStatus


def due_reminders_queryset():
    return Reminder.objects.filter(
        status=ReminderStatus.PENDING, remind_at__lte=timezone.now()
    ).select_related("owner", "application", "application__company")


def reminders_for_owner(owner):
    return Reminder.objects.filter(owner=owner).select_related(
        "application", "application__company"
    )
