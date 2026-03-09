from django.db import models

from core.models import OwnedModel, TimeStampedModel


class WeeklyGoal(OwnedModel, TimeStampedModel):
    week_start = models.DateField()
    target_applications = models.PositiveIntegerField(default=10)
    target_followups = models.PositiveIntegerField(default=5)
    target_interviews = models.PositiveIntegerField(default=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "week_start"], name="uniq_weekly_goal_per_owner"
            )
        ]
        ordering = ["-week_start"]
