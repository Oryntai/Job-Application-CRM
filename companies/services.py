from .models import Company


def upsert_company(owner, name: str, website: str = "", notes: str = "") -> Company:
    company, _ = Company.objects.update_or_create(
        owner=owner,
        name=name,
        defaults={"website": website, "notes": notes},
    )
    return company
