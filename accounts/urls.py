from django.urls import path

from .views import ProfileUpdateView

app_name = "accounts"

urlpatterns = [
    path("", ProfileUpdateView.as_view(), name="profile"),
]
