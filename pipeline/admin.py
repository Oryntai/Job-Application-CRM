from django.contrib import admin

from .models import ApplicationEvent, EventType


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    list_display = ("code", "label", "auto_status")


@admin.register(ApplicationEvent)
class ApplicationEventAdmin(admin.ModelAdmin):
    list_display = ("application", "event_type", "scheduled_at", "completed_at", "outcome")
    list_filter = ("event_type", "outcome")
