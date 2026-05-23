from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from .models import User


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "avatar", "bio"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 3}),
        }

class CustomAuthenticationForm(AuthenticationForm):
    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username and password:
            # 1. Attempt to find the user in the database
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                user = None

            # 2. If the user exists but is flagged as inactive, catch them here!
            if user is not None and not user.is_active:
                raise ValidationError(
                    "This account has been deactivated. Please contact your system administrator.",
                    code="inactive",
                )

        # 3. Otherwise, let Django run its standard username/password check
        return super().clean()