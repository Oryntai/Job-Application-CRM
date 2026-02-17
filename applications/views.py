from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import JobApplicationForm
from .models import ApplicationStatus, JobApplication, LocationType, Source
from .selectors import ApplicationFilters, filter_applications
from .services import InvalidStatusTransition, change_status


class ApplicationListView(LoginRequiredMixin, ListView):
    model = JobApplication
    template_name = "applications/list.html"
    context_object_name = "applications"
    paginate_by = 20

    def get_queryset(self):
        filters = ApplicationFilters(
            status=self.request.GET.get("status") or None,
            source=self.request.GET.get("source") or None,
            location_type=self.request.GET.get("location_type") or None,
            tag=self.request.GET.get("tag") or None,
            query=self.request.GET.get("q") or None,
        )
        ordering = self.request.GET.get("ordering", "-applied_date")
        return filter_applications(self.request.user, filters, ordering)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_choices"] = ApplicationStatus.choices
        context["source_choices"] = Source.choices
        context["location_choices"] = LocationType.choices
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get("HX-Request") == "true":
            return render(self.request, "applications/_application_list.html", context)
        return super().render_to_response(context, **response_kwargs)


class ApplicationDetailView(LoginRequiredMixin, DetailView):
    model = JobApplication
    template_name = "applications/detail.html"

    def get_queryset(self):
        return (
            JobApplication.objects.filter(owner=self.request.user)
            .select_related("company", "primary_contact")
            .prefetch_related("tags", "status_history", "events", "reminders")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_choices"] = ApplicationStatus.choices
        return context


class ApplicationCreateView(LoginRequiredMixin, CreateView):
    model = JobApplication
    form_class = JobApplicationForm
    template_name = "applications/form.html"
    success_url = reverse_lazy("applications:list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["owner"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        return response


class ApplicationUpdateView(LoginRequiredMixin, UpdateView):
    model = JobApplication
    form_class = JobApplicationForm
    template_name = "applications/form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["owner"] = self.request.user
        return kwargs

    def get_queryset(self):
        return JobApplication.objects.filter(owner=self.request.user)

    def get_success_url(self):
        return reverse("applications:detail", kwargs={"pk": self.object.pk})


class KanbanView(LoginRequiredMixin, ListView):
    model = JobApplication
    template_name = "applications/kanban.html"
    context_object_name = "applications"

    def get_queryset(self):
        return JobApplication.objects.filter(owner=self.request.user).select_related("company")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        grouped = {}
        for status, _ in ApplicationStatus.choices:
            grouped[status] = [a for a in context["applications"] if a.status == status]
        context["grouped"] = grouped
        context["statuses"] = ApplicationStatus.choices
        context["status_choices"] = ApplicationStatus.choices
        return context


@login_required
def move_status_view(request, pk: int):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")

    application = get_object_or_404(JobApplication, pk=pk, owner=request.user)
    to_status = request.POST.get("to_status")
    note = request.POST.get("note", "")

    if not to_status:
        return HttpResponseBadRequest("to_status is required")

    try:
        change_status(application, to_status, request.user, note)
    except InvalidStatusTransition as exc:
        return HttpResponseBadRequest(str(exc))

    if request.headers.get("HX-Request") == "true":
        return render(request, "applications/_application_card.html", {"application": application})
    return redirect("applications:kanban")
