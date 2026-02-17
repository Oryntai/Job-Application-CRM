import json
import logging
from datetime import timedelta
from urllib import parse, request

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone

from .models import NotificationLog, Reminder, ReminderChannel, ReminderStatus
from .selectors import due_reminders_queryset

logger = logging.getLogger(__name__)


def _send_email(reminder: Reminder) -> dict:
    subject = f"Job CRM reminder: {reminder.application.role_title}"
    body = (
        f"Company: {reminder.application.company.name}\n"
        f"Role: {reminder.application.role_title}\n"
        f"When: {reminder.remind_at.isoformat()}\n\n"
        f"Message: {reminder.message}"
    )
    recipient = reminder.owner.email or settings.DEFAULT_FROM_EMAIL
    sent = send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [recipient], fail_silently=False)
    return {"provider": "email", "sent": sent}


def _send_telegram(reminder: Reminder) -> dict:
    token = settings.TELEGRAM_TOKEN
    chat_id = (
        getattr(getattr(reminder.owner, "profile", None), "telegram_chat_id", "")
        or settings.TELEGRAM_CHAT_ID
    )
    if not token or not chat_id:
        raise RuntimeError("Telegram token or chat id is missing")

    text = f"Reminder: {reminder.application.role_title} at {reminder.application.company.name}\n{reminder.message}"
    payload = parse.urlencode({"chat_id": chat_id, "text": text}).encode()
    req = request.Request(f"https://api.telegram.org/bot{token}/sendMessage", data=payload)
    with request.urlopen(req, timeout=10) as resp:  # nosec B310
        return json.loads(resp.read().decode())


def _send_reminder(reminder: Reminder) -> dict:
    if reminder.channel == ReminderChannel.TELEGRAM:
        return _send_telegram(reminder)
    return _send_email(reminder)


@shared_task
def send_due_reminders() -> int:
    processed = 0
    for reminder in due_reminders_queryset():
        with transaction.atomic():
            try:
                provider_response = _send_reminder(reminder)
                reminder.status = ReminderStatus.SENT
                success = True
            except Exception as exc:  # noqa: BLE001
                logger.exception("Failed to send reminder", extra={"reminder_id": reminder.id})
                provider_response = {"error": str(exc)}
                reminder.status = ReminderStatus.FAILED
                success = False
            reminder.save(update_fields=["status", "updated_at"])
            NotificationLog.objects.create(
                reminder=reminder,
                provider_response=provider_response,
                success=success,
            )
            processed += 1
    return processed


@shared_task
def daily_digest() -> int:
    User = get_user_model()
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_start = today_start + timedelta(days=1)

    sent_count = 0
    for user in User.objects.filter(is_active=True):
        due = Reminder.objects.filter(
            owner=user,
            status=ReminderStatus.PENDING,
            remind_at__lt=tomorrow_start,
        ).select_related("application", "application__company")
        if not due.exists():
            continue

        lines = ["Today and overdue reminders:", ""]
        for item in due.order_by("remind_at"):
            flag = "OVERDUE" if item.remind_at < now else "TODAY"
            lines.append(
                f"[{flag}] {item.remind_at.isoformat()} - {item.application.role_title} @ {item.application.company.name}: {item.message}"
            )

        send_mail(
            "Job CRM daily digest",
            "\n".join(lines),
            settings.DEFAULT_FROM_EMAIL,
            [user.email or settings.DEFAULT_FROM_EMAIL],
            fail_silently=False,
        )
        sent_count += 1

    return sent_count
