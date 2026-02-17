from datetime import datetime

from django.db import transaction

from applications.models import JobApplication

from .models import Reminder


@transaction.atomic
def schedule_followup(
    application: JobApplication, remind_at: datetime, message: str, channel: str
) -> Reminder:
    reminder = Reminder.objects.create(
        owner=application.owner,
        application=application,
        remind_at=remind_at,
        message=message,
        channel=channel,
    )

    if application.next_action_at is None or remind_at < application.next_action_at:
        application.next_action_at = remind_at
        application.next_action_text = message[:255]
        application.save(update_fields=["next_action_at", "next_action_text", "updated_at"])

    return reminder
