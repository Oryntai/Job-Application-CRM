from datetime import timedelta

import pytest
from django.utils import timezone

from analytics.selectors import (
    get_dashboard_snapshot,
    get_funnel_stats,
    get_source_stats,
    get_time_in_stage,
)
from applications.models import ApplicationStatus, Source, StatusHistory
from tests.factories import JobApplicationFactory, UserFactory

pytestmark = pytest.mark.django_db


def test_get_funnel_stats_total_and_stages():
    user = UserFactory()
    JobApplicationFactory(owner=user, status=ApplicationStatus.APPLIED)
    JobApplicationFactory(owner=user, status=ApplicationStatus.INTERVIEW)

    stats = get_funnel_stats(user)

    assert stats["total_applications"] == 2
    assert stats["stages"][ApplicationStatus.APPLIED] == 2


def test_get_funnel_stats_conversion_values():
    user = UserFactory()
    JobApplicationFactory(owner=user, status=ApplicationStatus.APPLIED)
    JobApplicationFactory(owner=user, status=ApplicationStatus.SCREENING)

    stats = get_funnel_stats(user)

    assert stats["conversion"][ApplicationStatus.APPLIED] == 1.0
    assert 0 <= stats["conversion"][ApplicationStatus.SCREENING] <= 1


def test_get_time_in_stage_computes_aggregates():
    user = UserFactory()
    app = JobApplicationFactory(owner=user, status=ApplicationStatus.INTERVIEW)
    t1 = timezone.now() - timedelta(hours=10)
    t2 = timezone.now() - timedelta(hours=4)
    t3 = timezone.now()

    StatusHistory.objects.create(
        application=app,
        from_status="",
        to_status=ApplicationStatus.APPLIED,
        changed_by=user,
        changed_at=t1,
    )
    StatusHistory.objects.create(
        application=app,
        from_status=ApplicationStatus.APPLIED,
        to_status=ApplicationStatus.SCREENING,
        changed_by=user,
        changed_at=t2,
    )
    StatusHistory.objects.create(
        application=app,
        from_status=ApplicationStatus.SCREENING,
        to_status=ApplicationStatus.INTERVIEW,
        changed_by=user,
        changed_at=t3,
    )

    data = get_time_in_stage(user)

    assert ApplicationStatus.APPLIED in data
    assert data[ApplicationStatus.APPLIED]["samples"] == 1


def test_get_source_stats_counts_sources():
    user = UserFactory()
    JobApplicationFactory(owner=user, source=Source.HH)
    JobApplicationFactory(owner=user, source=Source.HH)
    JobApplicationFactory(owner=user, source=Source.LINKEDIN)

    stats = get_source_stats(user)

    assert stats[0]["source"] == Source.HH
    assert stats[0]["total"] == 2


def test_get_dashboard_snapshot_totals_and_due():
    user = UserFactory()
    JobApplicationFactory(owner=user, status=ApplicationStatus.OFFER)

    snapshot = get_dashboard_snapshot(user)

    assert snapshot["totals"]["offers"] == 1


def test_get_dashboard_snapshot_latest_changes_includes_history():
    user = UserFactory()
    app = JobApplicationFactory(owner=user)
    StatusHistory.objects.create(
        application=app,
        from_status=ApplicationStatus.DRAFT,
        to_status=ApplicationStatus.APPLIED,
        changed_by=user,
    )

    snapshot = get_dashboard_snapshot(user)

    assert len(snapshot["latest_changes"]) == 1
