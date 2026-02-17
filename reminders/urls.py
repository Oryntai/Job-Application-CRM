from django.urls import path

from .views import reminder_cancel_view, reminder_create_view, reminder_list_view

app_name = "reminders"

urlpatterns = [
    path("", reminder_list_view, name="list"),
    path("applications/<int:application_id>/new/", reminder_create_view, name="create"),
    path("<int:pk>/cancel/", reminder_cancel_view, name="cancel"),
]
