from .models import Profile


def update_notification_preferences(profile: Profile, email_notifications: bool, timezone: str):
    profile.email_notifications = email_notifications
    profile.timezone = timezone
    profile.save(update_fields=["email_notifications", "timezone", "updated_at"])
    return profile
