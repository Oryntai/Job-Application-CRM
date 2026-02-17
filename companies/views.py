from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import CompanyForm
from .models import Company
from .selectors import companies_for_owner


class CompanyListView(LoginRequiredMixin, ListView):
    model = Company
    template_name = "companies/list.html"
    context_object_name = "companies"

    def get_queryset(self):
        return companies_for_owner(self.request.user, self.request.GET.get("q", "")).annotate(
            jobs_count=Count("applications")
        )


class CompanyDetailView(LoginRequiredMixin, DetailView):
    model = Company
    template_name = "companies/detail.html"

    def get_queryset(self):
        return Company.objects.filter(owner=self.request.user).prefetch_related(
            "contacts", "jobapplication_set"
        )


class CompanyCreateView(LoginRequiredMixin, CreateView):
    model = Company
    form_class = CompanyForm
    template_name = "companies/form.html"
    success_url = reverse_lazy("companies:list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class CompanyUpdateView(LoginRequiredMixin, UpdateView):
    model = Company
    form_class = CompanyForm
    template_name = "companies/form.html"
    success_url = reverse_lazy("companies:list")

    def get_queryset(self):
        return Company.objects.filter(owner=self.request.user)
