from django.contrib import admin

from .models import NotificationLog, Reminder


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ("application", "owner", "remind_at", "channel", "status")
    list_filter = ("status", "channel")


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ("reminder", "sent_at", "success")
