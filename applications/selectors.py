from dataclasses import dataclass
from datetime import date

from django.db.models import Q

from .models import JobApplication


@dataclass
class ApplicationFilters:
    status: str | None = None
    source: str | None = None
    location_type: str | None = None
    tag: str | None = None
    date_from: date | None = None
    date_to: date | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    query: str | None = None


def application_queryset(owner):
    return (
        JobApplication.objects.filter(owner=owner)
        .select_related("company", "primary_contact")
        .prefetch_related("tags")
    )


def filter_applications(owner, filters: ApplicationFilters, ordering: str = "-applied_date"):
    qs = application_queryset(owner)
    if filters.status:
        qs = qs.filter(status=filters.status)
    if filters.source:
        qs = qs.filter(source=filters.source)
    if filters.location_type:
        qs = qs.filter(location_type=filters.location_type)
    if filters.tag:
        qs = qs.filter(tags__name__iexact=filters.tag)
    if filters.date_from:
        qs = qs.filter(applied_date__gte=filters.date_from)
    if filters.date_to:
        qs = qs.filter(applied_date__lte=filters.date_to)
    if filters.salary_min is not None:
        qs = qs.filter(salary_min__gte=filters.salary_min)
    if filters.salary_max is not None:
        qs = qs.filter(salary_max__lte=filters.salary_max)
    if filters.query:
        qs = qs.filter(
            Q(role_title__icontains=filters.query)
            | Q(company__name__icontains=filters.query)
            | Q(notes__icontains=filters.query)
        )
    return qs.distinct().order_by(ordering)
