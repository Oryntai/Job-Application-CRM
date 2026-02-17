from django.db import models

from core.models import OwnedModel, TimeStampedModel


class Company(OwnedModel, TimeStampedModel):
    name = models.CharField(max_length=255)
    website = models.URLField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["owner", "name"], name="uniq_company_per_owner"),
        ]
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Contact(OwnedModel, TimeStampedModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="contacts")
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=64, blank=True)
    title = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name
