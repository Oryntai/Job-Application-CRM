from collections import defaultdict
from datetime import date, timedelta
from statistics import mean, median

from django.db.models import Count, Q
from django.utils import timezone

from applications.models import ApplicationStatus, JobApplication, StatusHistory

from .models import WeeklyGoal

STAGE_ORDER = [
    ApplicationStatus.APPLIED,
    ApplicationStatus.SCREENING,
    ApplicationStatus.INTERVIEW,
    ApplicationStatus.OFFER,
]

STATUS_RANK = {
    ApplicationStatus.DRAFT: 0,
    ApplicationStatus.APPLIED: 1,
    ApplicationStatus.SCREENING: 2,
    ApplicationStatus.INTERVIEW: 3,
    ApplicationStatus.TEST_TASK: 3,
    ApplicationStatus.OFFER: 4,
    ApplicationStatus.REJECTED: 4,
    ApplicationStatus.WITHDRAWN: 4,
}


def _base_queryset(owner, date_range: tuple[date | None, date | None] | None = None):
    qs = JobApplication.objects.filter(owner=owner)
    if date_range:
        date_from, date_to = date_range
        if date_from:
            qs = qs.filter(applied_date__gte=date_from)
        if date_to:
            qs = qs.filter(applied_date__lte=date_to)
    return qs


def get_funnel_stats(owner, date_range: tuple[date | None, date | None] | None = None):
    apps = list(_base_queryset(owner, date_range).prefetch_related("status_history"))

    reached = {stage: 0 for stage in STAGE_ORDER}
    for app in apps:
        reached_statuses = {h.to_status for h in app.status_history.all()}
        current_rank = STATUS_RANK.get(app.status, 0)
        for stage in STAGE_ORDER:
            if stage in reached_statuses or current_rank >= STATUS_RANK[stage]:
                reached[stage] += 1

    conversion = {}
    prev = None
    for stage in STAGE_ORDER:
        count = reached[stage]
        conversion[stage] = 1.0 if prev is None else (count / prev if prev else 0.0)
        prev = count

    return {
        "total_applications": len(apps),
        "stages": reached,
        "conversion": conversion,
    }


def get_time_in_stage(owner):
    stage_durations = defaultdict(list)
    histories = (
        StatusHistory.objects.filter(application__owner=owner)
        .select_related("application")
        .order_by("application_id", "changed_at", "id")
    )

    by_app = defaultdict(list)
    for h in histories:
        by_app[h.application_id].append(h)

    for app_history in by_app.values():
        for idx in range(len(app_history) - 1):
            current = app_history[idx]
            nxt = app_history[idx + 1]
            if not current.to_status:
                continue
            hours = (nxt.changed_at - current.changed_at).total_seconds() / 3600
            if hours >= 0:
                stage_durations[current.to_status].append(hours)

    result = {}
    for stage, values in stage_durations.items():
        if values:
            result[stage] = {
                "avg_hours": round(mean(values), 2),
                "median_hours": round(median(values), 2),
                "samples": len(values),
            }

    return result


def get_source_stats(owner, date_range: tuple[date | None, date | None] | None = None):
    return list(
        _base_queryset(owner, date_range)
        .values("source")
        .annotate(total=Count("id"))
        .order_by("-total")
    )


def _week_start(value: date) -> date:
    return value - timedelta(days=value.weekday())


def get_or_create_current_weekly_goal(owner, today: date | None = None) -> WeeklyGoal:
    effective_today = today or timezone.localdate()
    week_start = _week_start(effective_today)
    goal, _ = WeeklyGoal.objects.get_or_create(
        owner=owner,
        week_start=week_start,
    )
    return goal


def get_weekly_goal_progress(owner, week_start: date | None = None):
    effective_week_start = week_start or _week_start(timezone.localdate())
    week_end = effective_week_start + timedelta(days=6)
    goal = WeeklyGoal.objects.filter(owner=owner, week_start=effective_week_start).first()
    if goal is None:
        goal = WeeklyGoal.objects.create(owner=owner, week_start=effective_week_start)

    applications_count = JobApplication.objects.filter(
        owner=owner,
        applied_date__gte=effective_week_start,
        applied_date__lte=week_end,
    ).count()

    from reminders.models import Reminder

    followups_count = Reminder.objects.filter(
        owner=owner,
        created_at__date__gte=effective_week_start,
        created_at__date__lte=week_end,
    ).count()

    interviews_count = (
        StatusHistory.objects.filter(
            application__owner=owner,
            to_status__in=[ApplicationStatus.INTERVIEW, ApplicationStatus.TEST_TASK],
            changed_at__date__gte=effective_week_start,
            changed_at__date__lte=week_end,
        )
        .values("application_id")
        .distinct()
        .count()
    )

    return {
        "week_start": effective_week_start,
        "week_end": week_end,
        "targets": {
            "applications": goal.target_applications,
            "followups": goal.target_followups,
            "interviews": goal.target_interviews,
        },
        "actual": {
            "applications": applications_count,
            "followups": followups_count,
            "interviews": interviews_count,
        },
        "completed": {
            "applications": applications_count >= goal.target_applications,
            "followups": followups_count >= goal.target_followups,
            "interviews": interviews_count >= goal.target_interviews,
        },
    }


def get_goal_streak(owner) -> int:
    current_week_start = _week_start(timezone.localdate())
    streak = 0
    cursor = current_week_start
    while True:
        progress = get_weekly_goal_progress(owner, cursor)
        if all(progress["completed"].values()):
            streak += 1
            cursor = cursor - timedelta(days=7)
            continue
        break
    return streak


def get_ab_outcomes(owner, date_range: tuple[date | None, date | None] | None = None):
    queryset = _base_queryset(owner, date_range)
    rows = list(
        queryset.values("outreach_variant").annotate(
            total=Count("id"),
            responses=Count(
                "id",
                filter=Q(
                    status__in=[
                        ApplicationStatus.SCREENING,
                        ApplicationStatus.INTERVIEW,
                        ApplicationStatus.TEST_TASK,
                        ApplicationStatus.OFFER,
                        ApplicationStatus.REJECTED,
                    ]
                ),
            ),
            interviews=Count(
                "id",
                filter=Q(
                    status__in=[
                        ApplicationStatus.INTERVIEW,
                        ApplicationStatus.TEST_TASK,
                        ApplicationStatus.OFFER,
                    ]
                ),
            ),
            offers=Count("id", filter=Q(status=ApplicationStatus.OFFER)),
        )
    )

    for row in rows:
        total = row["total"]
        row["response_rate"] = round((row["responses"] / total), 3) if total else 0.0
        row["interview_rate"] = round((row["interviews"] / total), 3) if total else 0.0
        row["offer_rate"] = round((row["offers"] / total), 3) if total else 0.0

    winner = None
    if rows:
        winner_row = sorted(
            rows, key=lambda item: (item["response_rate"], item["offer_rate"]), reverse=True
        )[0]
        winner = winner_row["outreach_variant"]

    return {
        "variants": rows,
        "winner": winner,
    }


def get_dashboard_snapshot(owner):
    from reminders.models import Reminder, ReminderStatus

    now = timezone.now()
    due_today = Reminder.objects.filter(
        owner=owner,
        status=ReminderStatus.PENDING,
        remind_at__date=now.date(),
    ).count()
    overdue = Reminder.objects.filter(
        owner=owner, status=ReminderStatus.PENDING, remind_at__lt=now
    ).count()
    latest_changes = (
        StatusHistory.objects.filter(application__owner=owner)
        .select_related("application")
        .order_by("-changed_at")[:10]
    )
    totals = JobApplication.objects.filter(owner=owner).aggregate(
        total=Count("id"),
        offers=Count("id", filter=Q(status=ApplicationStatus.OFFER)),
        rejected=Count("id", filter=Q(status=ApplicationStatus.REJECTED)),
    )
    weekly_goal = get_weekly_goal_progress(owner)
    weekly_streak = get_goal_streak(owner)
    ab_outcomes = get_ab_outcomes(owner)
    return {
        "due_today": due_today,
        "overdue": overdue,
        "latest_changes": latest_changes,
        "totals": totals,
        "weekly_goal": weekly_goal,
        "weekly_streak": weekly_streak,
        "ab_outcomes": ab_outcomes,
    }
