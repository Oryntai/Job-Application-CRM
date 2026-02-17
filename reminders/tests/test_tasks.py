from datetime import timedelta

import pytest
from django.core import mail
from django.utils import timezone

from reminders.models import NotificationLog, ReminderStatus
from reminders.tasks import daily_digest, send_due_reminders
from tests.factories import ReminderFactory, UserFactory

pytestmark = pytest.mark.django_db


def test_send_due_reminders_marks_sent_for_email(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    reminder = ReminderFactory(
        remind_at=timezone.now() - timedelta(minutes=2), status=ReminderStatus.PENDING
    )

    processed = send_due_reminders()

    reminder.refresh_from_db()
    assert processed == 1
    assert reminder.status == ReminderStatus.SENT
    assert NotificationLog.objects.filter(reminder=reminder, success=True).exists()


def test_send_due_reminders_marks_failed_on_telegram_without_config(settings):
    settings.TELEGRAM_TOKEN = ""
    settings.TELEGRAM_CHAT_ID = ""
    reminder = ReminderFactory(
        channel="TELEGRAM",
        remind_at=timezone.now() - timedelta(minutes=2),
        status=ReminderStatus.PENDING,
    )

    send_due_reminders()

    reminder.refresh_from_db()
    assert reminder.status == ReminderStatus.FAILED
    assert NotificationLog.objects.filter(reminder=reminder, success=False).exists()


def test_daily_digest_sends_email(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    user = UserFactory(email="digest@example.com")
    ReminderFactory(owner=user, remind_at=timezone.now(), status=ReminderStatus.PENDING)

    result = daily_digest()

    assert result == 1
    assert len(mail.outbox) == 1
    assert "daily digest" in mail.outbox[0].subject.lower()
