from django import forms
from .models import Client


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["name", "email", "company", "phone", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }
