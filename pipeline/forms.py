from django import forms

from .models import ApplicationEvent, EventType


class ApplicationEventForm(forms.ModelForm):
    event_type = forms.ModelChoiceField(queryset=EventType.objects.all())

    class Meta:
        model = ApplicationEvent
        fields = ["event_type", "scheduled_at", "completed_at", "outcome", "notes"]
        widgets = {
            "scheduled_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "completed_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }
