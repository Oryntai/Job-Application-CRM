from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from applications.models import JobApplication

from .forms import ReminderForm
from .models import Reminder, ReminderStatus
from .selectors import reminders_for_owner
from .services import schedule_followup


@login_required
def reminder_list_view(request):
    reminders = reminders_for_owner(request.user)
    return render(request, "reminders/list.html", {"reminders": reminders})


@login_required
def reminder_create_view(request, application_id: int):
    application = get_object_or_404(JobApplication, id=application_id, owner=request.user)
    if request.method == "POST":
        form = ReminderForm(request.POST)
        if form.is_valid():
            schedule_followup(
                application,
                form.cleaned_data["remind_at"],
                form.cleaned_data["message"],
                form.cleaned_data["channel"],
            )
            return redirect("applications:detail", pk=application.id)
    else:
        form = ReminderForm()
    return render(request, "reminders/form.html", {"form": form, "application": application})


@login_required
def reminder_cancel_view(request, pk: int):
    reminder = get_object_or_404(Reminder, pk=pk, owner=request.user)
    reminder.status = ReminderStatus.CANCELLED
    reminder.save(update_fields=["status", "updated_at"])
    return redirect("reminders:list")
