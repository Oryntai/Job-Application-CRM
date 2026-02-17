import pytest
from django.db import IntegrityError

from companies.models import Company
from tests.factories import CompanyFactory, ContactFactory, UserFactory

pytestmark = pytest.mark.django_db


def test_company_unique_per_owner_constraint():
    user = UserFactory()
    CompanyFactory(owner=user, name="Acme")

    with pytest.raises(IntegrityError):
        Company.objects.create(owner=user, name="Acme")


def test_company_same_name_allowed_for_different_owner():
    user1 = UserFactory()
    user2 = UserFactory()
    Company.objects.create(owner=user1, name="Acme")

    company = Company.objects.create(owner=user2, name="Acme")

    assert company.id is not None


def test_contact_belongs_to_company():
    contact = ContactFactory()

    assert contact.company is not None
