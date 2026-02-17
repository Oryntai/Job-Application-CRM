from datetime import timedelta

import pytest
from django.utils import timezone

from applications.models import ApplicationStatus, Source
from applications.selectors import ApplicationFilters, filter_applications
from tests.factories import JobApplicationFactory, TagFactory, UserFactory

pytestmark = pytest.mark.django_db


def test_filter_applications_by_status():
    user = UserFactory()
    JobApplicationFactory(owner=user, status=ApplicationStatus.APPLIED)
    JobApplicationFactory(owner=user, status=ApplicationStatus.INTERVIEW)

    result = filter_applications(user, ApplicationFilters(status=ApplicationStatus.INTERVIEW))

    assert result.count() == 1
    assert result.first().status == ApplicationStatus.INTERVIEW


def test_filter_applications_search_company_name():
    user = UserFactory()
    app = JobApplicationFactory(owner=user, company__name="Acme Rocket")
    JobApplicationFactory(owner=user, company__name="Other Corp")

    result = filter_applications(user, ApplicationFilters(query="Acme"))

    assert list(result) == [app]


def test_filter_applications_by_source():
    user = UserFactory()
    JobApplicationFactory(owner=user, source=Source.LINKEDIN)
    JobApplicationFactory(owner=user, source=Source.HH)

    result = filter_applications(user, ApplicationFilters(source=Source.HH))

    assert result.count() == 1
    assert result.first().source == Source.HH


def test_filter_applications_by_tag():
    user = UserFactory()
    tag = TagFactory(owner=user, name="ml")
    app = JobApplicationFactory(owner=user)
    app.tags.add(tag)
    JobApplicationFactory(owner=user)

    result = filter_applications(user, ApplicationFilters(tag="ml"))

    assert list(result) == [app]


def test_filter_applications_ordering_next_action():
    user = UserFactory()
    first = JobApplicationFactory(owner=user, next_action_at=timezone.now() + timedelta(days=2))
    second = JobApplicationFactory(owner=user, next_action_at=timezone.now() + timedelta(days=1))

    result = filter_applications(user, ApplicationFilters(), ordering="next_action_at")

    assert list(result)[:2] == [second, first]
