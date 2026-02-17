import pytest
from django.utils import timezone

from applications.models import ApplicationStatus
from pipeline.models import ApplicationEvent, EventCode, EventType
from pipeline.services import record_event
from tests.factories import JobApplicationFactory, UserFactory

pytestmark = pytest.mark.django_db


def test_record_event_creates_event():
    user = UserFactory()
    application = JobApplicationFactory(owner=user, status=ApplicationStatus.APPLIED)

    event = record_event(
        application, EventCode.OTHER, timezone.now(), notes="General update", user=user
    )

    assert ApplicationEvent.objects.filter(id=event.id).exists()
    assert event.event_type.code == EventCode.OTHER


def test_record_event_auto_changes_status_to_interview():
    user = UserFactory()
    application = JobApplicationFactory(owner=user, status=ApplicationStatus.APPLIED)

    record_event(application, EventCode.INTERVIEW, timezone.now(), user=user)

    application.refresh_from_db()
    assert application.status == ApplicationStatus.INTERVIEW


def test_record_event_invalid_auto_transition_is_ignored():
    user = UserFactory()
    application = JobApplicationFactory(owner=user, status=ApplicationStatus.REJECTED)

    record_event(application, EventCode.INTERVIEW, timezone.now(), user=user)

    application.refresh_from_db()
    assert application.status == ApplicationStatus.REJECTED


def test_record_event_creates_missing_event_type():
    user = UserFactory()
    application = JobApplicationFactory(owner=user)
    EventType.objects.filter(code=EventCode.OFFER_CALL).delete()

    record_event(application, EventCode.OFFER_CALL, timezone.now(), user=user)

    assert EventType.objects.filter(code=EventCode.OFFER_CALL).exists()
