from django.db import models
from django.utils import timezone

from applications.models import JobApplication
from core.models import TimeStampedModel


class EventCode(models.TextChoices):
    SCREENING_CALL = "SCREENING_CALL", "Screening Call"
    INTERVIEW = "INTERVIEW", "Interview"
    TEST_TASK = "TEST_TASK", "Test Task"
    OFFER_CALL = "OFFER_CALL", "Offer Call"
    OTHER = "OTHER", "Other"


class EventOutcome(models.TextChoices):
    PASS = "PASS", "Pass"
    FAIL = "FAIL", "Fail"
    NEUTRAL = "NEUTRAL", "Neutral"


class EventType(TimeStampedModel):
    code = models.CharField(max_length=32, choices=EventCode.choices, unique=True)
    label = models.CharField(max_length=100)
    auto_status = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ["code"]

    def __str__(self) -> str:
        return self.label


class ApplicationEvent(TimeStampedModel):
    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name="events")
    event_type = models.ForeignKey(EventType, on_delete=models.PROTECT, related_name="events")
    scheduled_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    outcome = models.CharField(max_length=10, choices=EventOutcome.choices, null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-scheduled_at", "-id"]

    @property
    def type(self) -> str:
        return self.event_type.code
