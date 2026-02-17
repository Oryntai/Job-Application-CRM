from django.urls import path

from .views import (
    ApplicationCreateView,
    ApplicationDetailView,
    ApplicationListView,
    ApplicationUpdateView,
    KanbanView,
    move_status_view,
)

app_name = "applications"

urlpatterns = [
    path("", ApplicationListView.as_view(), name="list"),
    path("new/", ApplicationCreateView.as_view(), name="create"),
    path("kanban/", KanbanView.as_view(), name="kanban"),
    path("<int:pk>/", ApplicationDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", ApplicationUpdateView.as_view(), name="edit"),
    path("<int:pk>/move-status/", move_status_view, name="move-status"),
]
