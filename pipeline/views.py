from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from applications.models import JobApplication

from .forms import ApplicationEventForm
from .services import record_event


@login_required
def add_event_view(request, application_id: int):
    application = get_object_or_404(JobApplication, id=application_id, owner=request.user)
    if request.method == "POST":
        form = ApplicationEventForm(request.POST)
        if form.is_valid():
            record_event(
                application=application,
                event_type_code=form.cleaned_data["event_type"].code,
                scheduled_at=form.cleaned_data["scheduled_at"],
                notes=form.cleaned_data.get("notes", ""),
                outcome=form.cleaned_data.get("outcome"),
                user=request.user,
            )
            return redirect("applications:detail", pk=application.id)
    else:
        form = ApplicationEventForm()
    return render(
        request, "applications/event_form.html", {"form": form, "application": application}
    )
