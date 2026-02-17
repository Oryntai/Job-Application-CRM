import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from applications.models import ApplicationStatus, JobApplication, Priority, Source
from companies.models import Company
from reminders.services import schedule_followup


class Command(BaseCommand):
    help = "Seed demo data for Job Application CRM"

    def add_arguments(self, parser):
        parser.add_argument("--username", default="demo")
        parser.add_argument("--password", default="demo12345")

    def handle(self, *args, **options):
        username = options["username"]
        password = options["password"]
        user_model = get_user_model()

        user, created = user_model.objects.get_or_create(
            username=username, defaults={"email": f"{username}@example.com"}
        )
        if created:
            user.set_password(password)
            user.save(update_fields=["password"])

        company_names = ["Acme", "Globex", "Initech", "Soylent", "Umbrella", "Stark Industries"]
        statuses = [
            ApplicationStatus.APPLIED,
            ApplicationStatus.SCREENING,
            ApplicationStatus.INTERVIEW,
            ApplicationStatus.TEST_TASK,
            ApplicationStatus.OFFER,
            ApplicationStatus.REJECTED,
        ]

        for idx, name in enumerate(company_names, start=1):
            company, _ = Company.objects.get_or_create(owner=user, name=name)
            app, _ = JobApplication.objects.get_or_create(
                owner=user,
                company=company,
                role_title=f"Python Developer {idx}",
                defaults={
                    "source": random.choice(Source.values),
                    "status": random.choice(statuses),
                    "priority": random.choice(Priority.values),
                    "applied_date": timezone.localdate() - timedelta(days=random.randint(1, 45)),
                },
            )
            remind_at = timezone.now() + timedelta(days=random.randint(-1, 3))
            schedule_followup(app, remind_at, "Follow up on application", "EMAIL")

        self.stdout.write(
            self.style.SUCCESS(f"Seeded data for user '{username}'. Password: {password}")
        )
