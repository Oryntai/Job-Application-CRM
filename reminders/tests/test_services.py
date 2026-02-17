from datetime import timedelta

import pytest
from django.utils import timezone

from reminders.models import ReminderStatus
from reminders.selectors import due_reminders_queryset
from reminders.services import schedule_followup
from tests.factories import JobApplicationFactory, ReminderFactory, UserFactory

pytestmark = pytest.mark.django_db


def test_schedule_followup_creates_reminder_with_owner():
    user = UserFactory()
    application = JobApplicationFactory(owner=user)

    reminder = schedule_followup(
        application, timezone.now() + timedelta(hours=2), "Ping recruiter", "EMAIL"
    )

    assert reminder.owner == user
    assert reminder.application == application


def test_schedule_followup_updates_next_action_when_empty():
    user = UserFactory()
    application = JobApplicationFactory(owner=user, next_action_at=None)
    remind_at = timezone.now() + timedelta(hours=2)

    schedule_followup(application, remind_at, "Ping recruiter", "EMAIL")

    application.refresh_from_db()
    assert application.next_action_at == remind_at
    assert application.next_action_text == "Ping recruiter"


def test_schedule_followup_updates_next_action_when_earlier():
    user = UserFactory()
    application = JobApplicationFactory(
        owner=user, next_action_at=timezone.now() + timedelta(days=3)
    )
    remind_at = timezone.now() + timedelta(hours=1)

    schedule_followup(application, remind_at, "Soon reminder", "EMAIL")

    application.refresh_from_db()
    assert application.next_action_at == remind_at


def test_schedule_followup_keeps_existing_next_action_when_later():
    user = UserFactory()
    current = timezone.now() + timedelta(hours=1)
    application = JobApplicationFactory(
        owner=user, next_action_at=current, next_action_text="Current"
    )

    schedule_followup(application, timezone.now() + timedelta(days=2), "Later reminder", "EMAIL")

    application.refresh_from_db()
    assert application.next_action_at == current
    assert application.next_action_text == "Current"


def test_due_reminders_queryset_returns_only_due_pending():
    user = UserFactory()
    due = ReminderFactory(
        owner=user, remind_at=timezone.now() - timedelta(minutes=1), status=ReminderStatus.PENDING
    )
    ReminderFactory(
        owner=user, remind_at=timezone.now() + timedelta(hours=1), status=ReminderStatus.PENDING
    )
    ReminderFactory(
        owner=user, remind_at=timezone.now() - timedelta(hours=1), status=ReminderStatus.SENT
    )

    ids = [r.id for r in due_reminders_queryset()]

    assert ids == [due.id]
