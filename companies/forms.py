from django import forms

from .models import Company, Contact


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ["name", "website", "notes"]


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ["company", "name", "email", "phone", "title", "notes"]

    def __init__(self, *args, owner=None, **kwargs):
        super().__init__(*args, **kwargs)
        if owner:
            self.fields["company"].queryset = Company.objects.filter(owner=owner)
