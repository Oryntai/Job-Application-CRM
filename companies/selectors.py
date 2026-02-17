from django.db.models import Q

from .models import Company, Contact


def companies_for_owner(owner, query: str = ""):
    qs = Company.objects.filter(owner=owner)
    if query:
        qs = qs.filter(
            Q(name__icontains=query) | Q(notes__icontains=query) | Q(website__icontains=query)
        )
    return qs


def contacts_for_owner(owner):
    return Contact.objects.filter(owner=owner).select_related("company")
