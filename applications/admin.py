from django.contrib import admin

from .models import Attachment, JobApplication, StatusHistory, Tag


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ("role_title", "company", "owner", "status", "priority", "applied_date")
    list_filter = ("status", "priority", "source", "location_type")
    search_fields = ("role_title", "company__name", "notes")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "owner")


@admin.register(StatusHistory)
class StatusHistoryAdmin(admin.ModelAdmin):
    list_display = ("application", "from_status", "to_status", "changed_at", "changed_by")


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ("name", "application", "owner", "created_at")
