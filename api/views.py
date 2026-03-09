from datetime import date

from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from analytics.models import WeeklyGoal
from analytics.selectors import (
    get_ab_outcomes,
    get_funnel_stats,
    get_goal_streak,
    get_time_in_stage,
    get_weekly_goal_progress,
)
from applications.models import JobApplication
from pipeline.api import ApplicationEventSerializer
from pipeline.models import ApplicationEvent
from reminders.api import ReminderSerializer
from reminders.models import Reminder
from reminders.services import schedule_followup


class OwnerApplicationMixin:
    def get_application(self):
        application_id = self.kwargs.get("application_id")
        if not application_id or getattr(self, "swagger_fake_view", False):
            return None
        return get_object_or_404(
            JobApplication,
            id=application_id,
            owner=self.request.user,
        )


class ApplicationEventListCreateAPIView(OwnerApplicationMixin, generics.ListCreateAPIView):
    serializer_class = ApplicationEventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        application = self.get_application()
        if application is None:
            return ApplicationEvent.objects.none()
        return ApplicationEvent.objects.filter(application=application).select_related("event_type")

    def perform_create(self, serializer):
        application = self.get_application()
        serializer.save(application=application)


class ApplicationEventDetailAPIView(OwnerApplicationMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ApplicationEventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        application = self.get_application()
        if application is None:
            return ApplicationEvent.objects.none()
        return ApplicationEvent.objects.filter(application=application).select_related("event_type")


class ApplicationReminderListCreateAPIView(OwnerApplicationMixin, generics.ListCreateAPIView):
    serializer_class = ReminderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        application = self.get_application()
        if application is None:
            return Reminder.objects.none()
        return Reminder.objects.filter(owner=self.request.user, application=application)

    def create(self, request, *args, **kwargs):
        application = self.get_application()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reminder = schedule_followup(
            application=application,
            remind_at=serializer.validated_data["remind_at"],
            message=serializer.validated_data["message"],
            channel=serializer.validated_data["channel"],
        )
        out = self.get_serializer(reminder)
        return Response(out.data, status=status.HTTP_201_CREATED)


class ApplicationReminderDetailAPIView(
    OwnerApplicationMixin, generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = ReminderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        application = self.get_application()
        if application is None:
            return Reminder.objects.none()
        return Reminder.objects.filter(owner=self.request.user, application=application)


@extend_schema(responses=OpenApiTypes.OBJECT)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def funnel_analytics_view(request):
    date_from = request.GET.get("from")
    date_to = request.GET.get("to")

    parsed_from = date.fromisoformat(date_from) if date_from else None
    parsed_to = date.fromisoformat(date_to) if date_to else None
    payload = get_funnel_stats(request.user, (parsed_from, parsed_to))
    return Response(payload)


@extend_schema(responses=OpenApiTypes.OBJECT)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def time_in_stage_analytics_view(request):
    payload = get_time_in_stage(request.user)
    return Response(payload)


@extend_schema(responses=OpenApiTypes.OBJECT)
@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def weekly_goal_analytics_view(request):
    if request.method == "PUT":
        week_start = request.data.get("week_start")
        parsed_week_start = date.fromisoformat(week_start) if week_start else None
        progress = get_weekly_goal_progress(request.user, parsed_week_start)
        goal = WeeklyGoal.objects.get(owner=request.user, week_start=progress["week_start"])
        goal.target_applications = int(
            request.data.get("target_applications", goal.target_applications)
        )
        goal.target_followups = int(request.data.get("target_followups", goal.target_followups))
        goal.target_interviews = int(request.data.get("target_interviews", goal.target_interviews))
        goal.save(
            update_fields=[
                "target_applications",
                "target_followups",
                "target_interviews",
                "updated_at",
            ]
        )

    week_start = request.GET.get("week_start")
    parsed_week_start = date.fromisoformat(week_start) if week_start else None
    payload = get_weekly_goal_progress(request.user, parsed_week_start)
    payload["streak_weeks"] = get_goal_streak(request.user)
    return Response(payload)


@extend_schema(responses=OpenApiTypes.OBJECT)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def ab_outcomes_analytics_view(request):
    date_from = request.GET.get("from")
    date_to = request.GET.get("to")
    parsed_from = date.fromisoformat(date_from) if date_from else None
    parsed_to = date.fromisoformat(date_to) if date_to else None
    payload = get_ab_outcomes(request.user, (parsed_from, parsed_to))
    return Response(payload)
