from applications.models import ApplicationStatus, JobApplication
from applications.services import InvalidStatusTransition, change_status

from .models import ApplicationEvent, EventCode, EventType

AUTO_STATUS_BY_EVENT = {
    EventCode.SCREENING_CALL: ApplicationStatus.SCREENING,
    EventCode.INTERVIEW: ApplicationStatus.INTERVIEW,
    EventCode.TEST_TASK: ApplicationStatus.TEST_TASK,
    EventCode.OFFER_CALL: ApplicationStatus.OFFER,
}


def record_event(
    application: JobApplication,
    event_type_code: str,
    scheduled_at,
    notes: str = "",
    outcome: str | None = None,
    user=None,
) -> ApplicationEvent:
    event_type, _ = EventType.objects.get_or_create(
        code=event_type_code, defaults={"label": event_type_code.replace("_", " ").title()}
    )
    event = ApplicationEvent.objects.create(
        application=application,
        event_type=event_type,
        scheduled_at=scheduled_at,
        notes=notes,
        outcome=outcome,
    )

    auto_status = AUTO_STATUS_BY_EVENT.get(event_type.code)
    if auto_status and application.status != auto_status:
        try:
            change_status(application, auto_status, user, f"Auto by event {event_type.code}")
        except InvalidStatusTransition:
            pass

    return event
