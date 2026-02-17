from django import forms

from .models import Reminder


class ReminderForm(forms.ModelForm):
    class Meta:
        model = Reminder
        fields = ["remind_at", "channel", "message"]
        widgets = {
            "remind_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }
