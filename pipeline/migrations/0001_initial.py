import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


def seed_event_types(apps, schema_editor):
    EventType = apps.get_model("pipeline", "EventType")
    rows = [
        ("SCREENING_CALL", "Screening Call", "SCREENING"),
        ("INTERVIEW", "Interview", "INTERVIEW"),
        ("TEST_TASK", "Test Task", "TEST_TASK"),
        ("OFFER_CALL", "Offer Call", "OFFER"),
        ("OTHER", "Other", ""),
    ]
    for code, label, auto_status in rows:
        EventType.objects.get_or_create(
            code=code, defaults={"label": label, "auto_status": auto_status}
        )


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("applications", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="EventType",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "code",
                    models.CharField(
                        choices=[
                            ("SCREENING_CALL", "Screening Call"),
                            ("INTERVIEW", "Interview"),
                            ("TEST_TASK", "Test Task"),
                            ("OFFER_CALL", "Offer Call"),
                            ("OTHER", "Other"),
                        ],
                        max_length=32,
                        unique=True,
                    ),
                ),
                ("label", models.CharField(max_length=100)),
                ("auto_status", models.CharField(blank=True, max_length=20)),
            ],
            options={"ordering": ["code"]},
        ),
        migrations.CreateModel(
            name="ApplicationEvent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("scheduled_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "outcome",
                    models.CharField(
                        blank=True,
                        choices=[("PASS", "Pass"), ("FAIL", "Fail"), ("NEUTRAL", "Neutral")],
                        max_length=10,
                        null=True,
                    ),
                ),
                ("notes", models.TextField(blank=True)),
                (
                    "application",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="events",
                        to="applications.jobapplication",
                    ),
                ),
                (
                    "event_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="events",
                        to="pipeline.eventtype",
                    ),
                ),
            ],
            options={"ordering": ["-scheduled_at", "-id"]},
        ),
        migrations.RunPython(seed_event_types, migrations.RunPython.noop),
    ]
