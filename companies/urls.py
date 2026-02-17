from django.urls import path

from .views import CompanyCreateView, CompanyDetailView, CompanyListView, CompanyUpdateView

app_name = "companies"

urlpatterns = [
    path("", CompanyListView.as_view(), name="list"),
    path("new/", CompanyCreateView.as_view(), name="create"),
    path("<int:pk>/", CompanyDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", CompanyUpdateView.as_view(), name="edit"),
]
