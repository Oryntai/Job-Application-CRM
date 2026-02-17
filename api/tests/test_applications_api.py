import pytest
from rest_framework.test import APIClient

from applications.models import ApplicationStatus
from tests.factories import CompanyFactory, JobApplicationFactory, UserFactory

pytestmark = pytest.mark.django_db


def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def test_applications_list_returns_only_owner_items():
    user = UserFactory()
    other = UserFactory()
    own = JobApplicationFactory(owner=user)
    JobApplicationFactory(owner=other)

    response = auth_client(user).get("/api/v1/applications/")

    assert response.status_code == 200
    ids = [item["id"] for item in response.json()["results"]]
    assert own.id in ids
    assert len(ids) == 1


def test_create_application_success():
    user = UserFactory()
    company = CompanyFactory(owner=user)
    payload = {
        "company": company.id,
        "role_title": "Backend Engineer",
        "source": "LINKEDIN",
        "status": "APPLIED",
        "priority": "HIGH",
        "applied_date": "2026-02-01",
    }

    response = auth_client(user).post("/api/v1/applications/", payload, format="json")

    assert response.status_code == 201
    assert response.json()["role_title"] == "Backend Engineer"


def test_update_application_success():
    user = UserFactory()
    app = JobApplicationFactory(owner=user)

    response = auth_client(user).patch(
        f"/api/v1/applications/{app.id}/",
        {"status": ApplicationStatus.APPLIED},
        format="json",
    )

    assert response.status_code == 200
    assert response.json()["status"] == ApplicationStatus.APPLIED


def test_nested_events_create_and_list():
    user = UserFactory()
    app = JobApplicationFactory(owner=user)
    client = auth_client(user)

    create = client.post(
        f"/api/v1/applications/{app.id}/events/",
        {
            "application": app.id,
            "event_type_code": "INTERVIEW",
            "scheduled_at": "2026-02-03T10:00:00Z",
            "notes": "tech round",
        },
        format="json",
    )
    listed = client.get(f"/api/v1/applications/{app.id}/events/")

    assert create.status_code == 201
    assert listed.status_code == 200
    assert len(listed.json()["results"]) == 1


def test_nested_reminders_create_and_list():
    user = UserFactory()
    app = JobApplicationFactory(owner=user)
    client = auth_client(user)

    create = client.post(
        f"/api/v1/applications/{app.id}/reminders/",
        {
            "application": app.id,
            "remind_at": "2026-02-03T10:00:00Z",
            "channel": "EMAIL",
            "message": "follow up",
        },
        format="json",
    )
    listed = client.get(f"/api/v1/applications/{app.id}/reminders/")

    assert create.status_code == 201
    assert listed.status_code == 200
    assert len(listed.json()["results"]) == 1


def test_analytics_endpoints_accessible():
    user = UserFactory()
    JobApplicationFactory(owner=user)
    client = auth_client(user)

    funnel = client.get("/api/v1/analytics/funnel")
    time_in_stage = client.get("/api/v1/analytics/time-in-stage")

    assert funnel.status_code == 200
    assert time_in_stage.status_code == 200


def test_owner_cannot_access_other_users_nested_resources():
    user = UserFactory()
    other = UserFactory()
    app = JobApplicationFactory(owner=other)

    response = auth_client(user).get(f"/api/v1/applications/{app.id}/events/")

    assert response.status_code == 404


def test_companies_crud_owner_scope():
    user = UserFactory()
    other = UserFactory()
    CompanyFactory(owner=other)
    client = auth_client(user)

    created = client.post(
        "/api/v1/companies/", {"name": "Acme", "website": "https://acme.dev"}, format="json"
    )
    listed = client.get("/api/v1/companies/")

    assert created.status_code == 201
    assert listed.status_code == 200
    assert listed.json()["count"] == 1
