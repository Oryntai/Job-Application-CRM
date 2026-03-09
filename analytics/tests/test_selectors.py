from datetime import timedelta

import pytest
from django.utils import timezone

from analytics.selectors import (
    get_ab_outcomes,
    get_dashboard_snapshot,
    get_funnel_stats,
    get_goal_streak,
    get_source_stats,
    get_time_in_stage,
    get_weekly_goal_progress,
)
from applications.models import ApplicationStatus, OutreachVariant, Source, StatusHistory
from tests.factories import JobApplicationFactory, ReminderFactory, UserFactory, WeeklyGoalFactory

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


def test_get_weekly_goal_progress_uses_current_week_data():
    user = UserFactory()
    WeeklyGoalFactory(owner=user, target_applications=1, target_followups=1, target_interviews=0)
    JobApplicationFactory(owner=user)
    ReminderFactory(owner=user)

    progress = get_weekly_goal_progress(user)

    assert progress["actual"]["applications"] >= 1
    assert progress["actual"]["followups"] >= 1


def test_get_goal_streak_counts_consecutive_completed_weeks():
    user = UserFactory()
    current = timezone.localdate() - timedelta(days=timezone.localdate().weekday())
    previous = current - timedelta(days=7)
    WeeklyGoalFactory(
        owner=user,
        week_start=current,
        target_applications=1,
        target_followups=0,
        target_interviews=0,
    )
    WeeklyGoalFactory(
        owner=user,
        week_start=previous,
        target_applications=1,
        target_followups=0,
        target_interviews=0,
    )
    JobApplicationFactory(owner=user, applied_date=current)
    JobApplicationFactory(owner=user, applied_date=previous)

    streak = get_goal_streak(user)

    assert streak == 2


def test_get_ab_outcomes_returns_rates_and_winner():
    user = UserFactory()
    JobApplicationFactory(
        owner=user,
        outreach_variant=OutreachVariant.A,
        status=ApplicationStatus.SCREENING,
    )
    JobApplicationFactory(
        owner=user,
        outreach_variant=OutreachVariant.B,
        status=ApplicationStatus.DRAFT,
    )

    payload = get_ab_outcomes(user)

    assert len(payload["variants"]) == 2
    assert payload["winner"] == OutreachVariant.A
