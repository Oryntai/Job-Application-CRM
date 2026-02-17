import pytest

from applications.models import ApplicationStatus, StatusHistory
from applications.services import InvalidStatusTransition, change_status
from tests.factories import JobApplicationFactory, UserFactory

pytestmark = pytest.mark.django_db


def test_change_status_creates_history_entry():
    user = UserFactory()
    application = JobApplicationFactory(owner=user, status=ApplicationStatus.DRAFT)

    change_status(application, ApplicationStatus.APPLIED, user, note="Applied now")

    application.refresh_from_db()
    assert application.status == ApplicationStatus.APPLIED
    history = StatusHistory.objects.get(application=application)
    assert history.from_status == ApplicationStatus.DRAFT
    assert history.to_status == ApplicationStatus.APPLIED


def test_change_status_rejects_invalid_transition():
    user = UserFactory()
    application = JobApplicationFactory(owner=user, status=ApplicationStatus.DRAFT)

    with pytest.raises(InvalidStatusTransition):
        change_status(application, ApplicationStatus.OFFER, user)


def test_change_status_same_status_no_history_created():
    user = UserFactory()
    application = JobApplicationFactory(owner=user, status=ApplicationStatus.APPLIED)

    change_status(application, ApplicationStatus.APPLIED, user)

    assert StatusHistory.objects.filter(application=application).count() == 0


def test_change_status_applied_to_interview_allowed():
    user = UserFactory()
    application = JobApplicationFactory(owner=user, status=ApplicationStatus.APPLIED)

    change_status(application, ApplicationStatus.INTERVIEW, user)

    application.refresh_from_db()
    assert application.status == ApplicationStatus.INTERVIEW


def test_change_status_rejected_terminal():
    user = UserFactory()
    application = JobApplicationFactory(owner=user, status=ApplicationStatus.REJECTED)

    with pytest.raises(InvalidStatusTransition):
        change_status(application, ApplicationStatus.OFFER, user)


def test_change_status_note_saved():
    user = UserFactory()
    application = JobApplicationFactory(owner=user, status=ApplicationStatus.APPLIED)

    change_status(application, ApplicationStatus.SCREENING, user, note="Recruiter call")

    history = StatusHistory.objects.get(application=application)
    assert history.note == "Recruiter call"


def test_change_status_changed_by_saved():
    user = UserFactory()
    application = JobApplicationFactory(owner=user, status=ApplicationStatus.APPLIED)

    change_status(application, ApplicationStatus.SCREENING, user)

    history = StatusHistory.objects.get(application=application)
    assert history.changed_by == user


def test_change_status_multiple_histories_create_records():
    user = UserFactory()
    application = JobApplicationFactory(owner=user, status=ApplicationStatus.DRAFT)

    change_status(application, ApplicationStatus.APPLIED, user)
    change_status(application, ApplicationStatus.SCREENING, user)

    assert StatusHistory.objects.filter(application=application).count() == 2
