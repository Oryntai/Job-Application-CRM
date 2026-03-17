from django.urls import path

from .views import ProfileUpdateView, SignUpView

app_name = "accounts"

urlpatterns = [
    path("profile/", ProfileUpdateView.as_view(), name="profile"),
    path("signup/", SignUpView.as_view(), name="signup"),
]
