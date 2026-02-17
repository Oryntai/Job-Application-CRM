from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from companies.models import Company, Contact
from core.models import OwnedModel, TimeStampedModel


class Source(models.TextChoices):
    HH = "HH", "HeadHunter"
    LINKEDIN = "LINKEDIN", "LinkedIn"
    REFERRAL = "REFERRAL", "Referral"
    COMPANY_SITE = "COMPANY_SITE", "Company Site"
    OTHER = "OTHER", "Other"


class LocationType(models.TextChoices):
    REMOTE = "REMOTE", "Remote"
    HYBRID = "HYBRID", "Hybrid"
    ONSITE = "ONSITE", "Onsite"


class ApplicationStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    APPLIED = "APPLIED", "Applied"
    SCREENING = "SCREENING", "Screening"
    INTERVIEW = "INTERVIEW", "Interview"
    TEST_TASK = "TEST_TASK", "Test Task"
    OFFER = "OFFER", "Offer"
    REJECTED = "REJECTED", "Rejected"
    WITHDRAWN = "WITHDRAWN", "Withdrawn"


class Priority(models.TextChoices):
    LOW = "LOW", "Low"
    MED = "MED", "Medium"
    HIGH = "HIGH", "High"


class Currency(models.TextChoices):
    USD = "USD", "USD"
    EUR = "EUR", "EUR"
    RUB = "RUB", "RUB"


class Tag(OwnedModel, TimeStampedModel):
    name = models.CharField(max_length=100)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["owner", "name"], name="uniq_tag_per_owner")]
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class JobApplication(OwnedModel, TimeStampedModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="applications")
    primary_contact = models.ForeignKey(
        Contact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="primary_applications",
    )
    role_title = models.CharField(max_length=255)
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.OTHER)
    job_url = models.URLField(blank=True)
    location_type = models.CharField(
        max_length=10, choices=LocationType.choices, default=LocationType.REMOTE
    )
    location_text = models.CharField(max_length=255, blank=True)
    salary_min = models.PositiveIntegerField(null=True, blank=True)
    salary_max = models.PositiveIntegerField(null=True, blank=True)
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.USD)
    applied_date = models.DateField(default=timezone.localdate)
    status = models.CharField(
        max_length=20, choices=ApplicationStatus.choices, default=ApplicationStatus.DRAFT
    )
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MED)
    notes = models.TextField(blank=True)
    next_action_at = models.DateTimeField(null=True, blank=True)
    next_action_text = models.CharField(max_length=255, blank=True)
    tags = models.ManyToManyField(
        Tag, through="ApplicationTag", related_name="applications", blank=True
    )

    class Meta:
        ordering = ["-applied_date", "-updated_at"]

    def clean(self):
        if (
            self.salary_min is not None
            and self.salary_max is not None
            and self.salary_min > self.salary_max
        ):
            raise ValidationError(
                {"salary_min": "salary_min must be less than or equal salary_max"}
            )

    def __str__(self) -> str:
        return f"{self.role_title} @ {self.company.name}"


class ApplicationTag(TimeStampedModel):
    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["application", "tag"], name="uniq_application_tag")
        ]


class StatusHistory(TimeStampedModel):
    application = models.ForeignKey(
        JobApplication, on_delete=models.CASCADE, related_name="status_history"
    )
    from_status = models.CharField(max_length=20, choices=ApplicationStatus.choices, blank=True)
    to_status = models.CharField(max_length=20, choices=ApplicationStatus.choices)
    changed_at = models.DateTimeField(default=timezone.now)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-changed_at", "-id"]


class Attachment(OwnedModel, TimeStampedModel):
    application = models.ForeignKey(
        JobApplication, on_delete=models.CASCADE, related_name="attachments"
    )
    file = models.FileField(upload_to="attachments/")
    name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ["-created_at"]
