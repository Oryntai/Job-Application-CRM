import factory
from django.contrib.auth import get_user_model
from django.utils import timezone

from applications.models import (
    ApplicationStatus,
    JobApplication,
    Priority,
    Source,
    Tag,
)
from companies.models import Company, Contact
from pipeline.models import ApplicationEvent, EventCode, EventType
from reminders.models import Reminder, ReminderChannel, ReminderStatus


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "password123")


class CompanyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Company

    owner = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: f"Company {n}")
    website = factory.Sequence(lambda n: f"https://company{n}.example.com")


class ContactFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Contact

    owner = factory.SelfAttribute("company.owner")
    company = factory.SubFactory(CompanyFactory)
    name = factory.Sequence(lambda n: f"Contact {n}")
    email = factory.Sequence(lambda n: f"contact{n}@example.com")


class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tag

    owner = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: f"tag-{n}")


class JobApplicationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = JobApplication

    owner = factory.SubFactory(UserFactory)
    company = factory.SubFactory(CompanyFactory, owner=factory.SelfAttribute("..owner"))
    role_title = factory.Sequence(lambda n: f"Python Engineer {n}")
    source = Source.LINKEDIN
    status = ApplicationStatus.DRAFT
    priority = Priority.MED
    applied_date = factory.LazyFunction(timezone.localdate)


class EventTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EventType

    code = EventCode.INTERVIEW
    label = "Interview"


class ApplicationEventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ApplicationEvent

    application = factory.SubFactory(JobApplicationFactory)
    event_type = factory.SubFactory(EventTypeFactory)
    scheduled_at = factory.LazyFunction(timezone.now)


class ReminderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Reminder

    owner = factory.SubFactory(UserFactory)
    application = factory.SubFactory(JobApplicationFactory, owner=factory.SelfAttribute("..owner"))
    remind_at = factory.LazyFunction(timezone.now)
    channel = ReminderChannel.EMAIL
    message = "Follow up"
    status = ReminderStatus.PENDING
