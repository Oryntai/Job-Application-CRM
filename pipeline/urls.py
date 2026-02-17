from django.urls import path

from .views import add_event_view

app_name = "pipeline"

urlpatterns = [
    path("applications/<int:application_id>/events/new/", add_event_view, name="event-create"),
]
