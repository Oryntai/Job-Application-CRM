import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("companies", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="JobApplication",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("role_title", models.CharField(max_length=255)),
                (
                    "source",
                    models.CharField(
                        choices=[
                            ("HH", "HeadHunter"),
                            ("LINKEDIN", "LinkedIn"),
                            ("REFERRAL", "Referral"),
                            ("COMPANY_SITE", "Company Site"),
                            ("OTHER", "Other"),
                        ],
                        default="OTHER",
                        max_length=20,
                    ),
                ),
                ("job_url", models.URLField(blank=True)),
                (
                    "location_type",
                    models.CharField(
                        choices=[("REMOTE", "Remote"), ("HYBRID", "Hybrid"), ("ONSITE", "Onsite")],
                        default="REMOTE",
                        max_length=10,
                    ),
                ),
                ("location_text", models.CharField(blank=True, max_length=255)),
                ("salary_min", models.PositiveIntegerField(blank=True, null=True)),
                ("salary_max", models.PositiveIntegerField(blank=True, null=True)),
                (
                    "currency",
                    models.CharField(
                        choices=[("USD", "USD"), ("EUR", "EUR"), ("RUB", "RUB")],
                        default="USD",
                        max_length=3,
                    ),
                ),
                ("applied_date", models.DateField(default=django.utils.timezone.localdate)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("DRAFT", "Draft"),
                            ("APPLIED", "Applied"),
                            ("SCREENING", "Screening"),
                            ("INTERVIEW", "Interview"),
                            ("TEST_TASK", "Test Task"),
                            ("OFFER", "Offer"),
                            ("REJECTED", "Rejected"),
                            ("WITHDRAWN", "Withdrawn"),
                        ],
                        default="DRAFT",
                        max_length=20,
                    ),
                ),
                (
                    "priority",
                    models.CharField(
                        choices=[("LOW", "Low"), ("MED", "Medium"), ("HIGH", "High")],
                        default="MED",
                        max_length=10,
                    ),
                ),
                ("notes", models.TextField(blank=True)),
                ("next_action_at", models.DateTimeField(blank=True, null=True)),
                ("next_action_text", models.CharField(blank=True, max_length=255)),
                (
                    "company",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="applications",
                        to="companies.company",
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
                    ),
                ),
                (
                    "primary_contact",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="primary_applications",
                        to="companies.contact",
                    ),
                ),
            ],
            options={"ordering": ["-applied_date", "-updated_at"]},
        ),
        migrations.CreateModel(
            name="Tag",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=100)),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="StatusHistory",
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
                    "from_status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("DRAFT", "Draft"),
                            ("APPLIED", "Applied"),
                            ("SCREENING", "Screening"),
                            ("INTERVIEW", "Interview"),
                            ("TEST_TASK", "Test Task"),
                            ("OFFER", "Offer"),
                            ("REJECTED", "Rejected"),
                            ("WITHDRAWN", "Withdrawn"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "to_status",
                    models.CharField(
                        choices=[
                            ("DRAFT", "Draft"),
                            ("APPLIED", "Applied"),
                            ("SCREENING", "Screening"),
                            ("INTERVIEW", "Interview"),
                            ("TEST_TASK", "Test Task"),
                            ("OFFER", "Offer"),
                            ("REJECTED", "Rejected"),
                            ("WITHDRAWN", "Withdrawn"),
                        ],
                        max_length=20,
                    ),
                ),
                ("changed_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("note", models.CharField(blank=True, max_length=255)),
                (
                    "application",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="status_history",
                        to="applications.jobapplication",
                    ),
                ),
                (
                    "changed_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"ordering": ["-changed_at", "-id"]},
        ),
        migrations.CreateModel(
            name="Attachment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("file", models.FileField(upload_to="attachments/")),
                ("name", models.CharField(max_length=255)),
                ("content_type", models.CharField(blank=True, max_length=120)),
                (
                    "application",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attachments",
                        to="applications.jobapplication",
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="ApplicationTag",
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
                    "application",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="applications.jobapplication",
                    ),
                ),
                (
                    "tag",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="applications.tag"
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="jobapplication",
            name="tags",
            field=models.ManyToManyField(
                blank=True,
                related_name="applications",
                through="applications.ApplicationTag",
                to="applications.tag",
            ),
        ),
        migrations.AddConstraint(
            model_name="tag",
            constraint=models.UniqueConstraint(fields=("owner", "name"), name="uniq_tag_per_owner"),
        ),
        migrations.AddConstraint(
            model_name="applicationtag",
            constraint=models.UniqueConstraint(
                fields=("application", "tag"), name="uniq_application_tag"
            ),
        ),
    ]
