from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts.api import ProfileViewSet
from applications.api import JobApplicationViewSet, TagViewSet
from companies.api import CompanyViewSet, ContactViewSet

from .views import (
    ApplicationEventDetailAPIView,
    ApplicationEventListCreateAPIView,
    ApplicationReminderDetailAPIView,
    ApplicationReminderListCreateAPIView,
    funnel_analytics_view,
    time_in_stage_analytics_view,
)

router = DefaultRouter()
router.register("applications", JobApplicationViewSet, basename="applications")
router.register("companies", CompanyViewSet, basename="companies")
router.register("contacts", ContactViewSet, basename="contacts")
router.register("tags", TagViewSet, basename="tags")
router.register("profiles", ProfileViewSet, basename="profiles")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path(
        "applications/<int:application_id>/events/",
        ApplicationEventListCreateAPIView.as_view(),
        name="application-events",
    ),
    path(
        "applications/<int:application_id>/events/<int:pk>/",
        ApplicationEventDetailAPIView.as_view(),
        name="application-event-detail",
    ),
    path(
        "applications/<int:application_id>/reminders/",
        ApplicationReminderListCreateAPIView.as_view(),
        name="application-reminders",
    ),
    path(
        "applications/<int:application_id>/reminders/<int:pk>/",
        ApplicationReminderDetailAPIView.as_view(),
        name="application-reminder-detail",
    ),
    path("analytics/funnel", funnel_analytics_view, name="analytics-funnel"),
    path("analytics/time-in-stage", time_in_stage_analytics_view, name="analytics-time-in-stage"),
]
