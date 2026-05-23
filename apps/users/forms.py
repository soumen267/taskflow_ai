from django import forms
from apps.accounts.models import User

class UserForm(forms.ModelForm):
    # 1. Use PasswordInput widget so the password appears as dots (•••••) instead of raw text
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        help_text="Password will be automatically encrypted using PBKDF2 hashing."
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password", "avatar"]

    # 2. OVERRIDE THE SAVE METHOD: This intercepts the form before writing to the database
    def save(self, commit=True):
        # Call the parent form save, but don't commit to the database yet
        user = super().save(commit=False)
        
        # Pull the clean password string out of your form submission
        raw_password = self.cleaned_data.get("password")
        
        if raw_password:
            # ✅ THIS IS THE MAGIC: Encrypts the raw password automatically!
            user.set_password(raw_password)
            
        if commit:
            user.save() # Now it is safe to save to your database table
            
        return user