from django.db import transaction
from django.utils import timezone

from .models import ApplicationStatus, JobApplication, StatusHistory

ALLOWED_TRANSITIONS = {
    ApplicationStatus.DRAFT: {ApplicationStatus.APPLIED, ApplicationStatus.WITHDRAWN},
    ApplicationStatus.APPLIED: {
        ApplicationStatus.SCREENING,
        ApplicationStatus.INTERVIEW,
        ApplicationStatus.TEST_TASK,
        ApplicationStatus.REJECTED,
        ApplicationStatus.WITHDRAWN,
        ApplicationStatus.OFFER,
    },
    ApplicationStatus.SCREENING: {
        ApplicationStatus.INTERVIEW,
        ApplicationStatus.TEST_TASK,
        ApplicationStatus.REJECTED,
        ApplicationStatus.WITHDRAWN,
        ApplicationStatus.OFFER,
    },
    ApplicationStatus.INTERVIEW: {
        ApplicationStatus.OFFER,
        ApplicationStatus.REJECTED,
        ApplicationStatus.WITHDRAWN,
        ApplicationStatus.TEST_TASK,
    },
    ApplicationStatus.TEST_TASK: {
        ApplicationStatus.INTERVIEW,
        ApplicationStatus.OFFER,
        ApplicationStatus.REJECTED,
        ApplicationStatus.WITHDRAWN,
    },
    ApplicationStatus.OFFER: {ApplicationStatus.WITHDRAWN, ApplicationStatus.REJECTED},
    ApplicationStatus.REJECTED: set(),
    ApplicationStatus.WITHDRAWN: set(),
}


class InvalidStatusTransition(Exception):
    pass


@transaction.atomic
def change_status(
    application: JobApplication, to_status: str, user, note: str | None = None
) -> JobApplication:
    current = application.status
    if to_status == current:
        return application

    allowed = ALLOWED_TRANSITIONS.get(current, set())
    if to_status not in allowed:
        raise InvalidStatusTransition(f"Transition {current} -> {to_status} is not allowed")

    application.status = to_status
    application.updated_at = timezone.now()
    application.save(update_fields=["status", "updated_at"])

    StatusHistory.objects.create(
        application=application,
        from_status=current,
        to_status=to_status,
        changed_by=user,
        note=note or "",
    )
    return application
