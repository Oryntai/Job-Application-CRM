from django import forms

from companies.models import Company, Contact

from .models import ApplicationStatus, JobApplication


class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = [
            "company",
            "primary_contact",
            "role_title",
            "source",
            "job_url",
            "location_type",
            "location_text",
            "salary_min",
            "salary_max",
            "currency",
            "applied_date",
            "status",
            "priority",
            "notes",
            "next_action_at",
            "next_action_text",
            "tags",
        ]
        widgets = {
            "applied_date": forms.DateInput(attrs={"type": "date"}),
            "next_action_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "notes": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, owner=None, **kwargs):
        super().__init__(*args, **kwargs)
        if owner:
            self.fields["company"].queryset = Company.objects.filter(owner=owner)
            self.fields["primary_contact"].queryset = Contact.objects.filter(owner=owner)
            self.fields["tags"].queryset = self.fields["tags"].queryset.filter(owner=owner)


class StatusMoveForm(forms.Form):
    to_status = forms.ChoiceField(choices=ApplicationStatus.choices)
    note = forms.CharField(max_length=255, required=False)
