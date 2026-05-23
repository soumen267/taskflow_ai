from django import forms
from apps.accounts.models import User
from apps.clients.models import Client  # ✅ 1. IMPORT YOUR CLIENT MODEL
from django.utils import timezone
from .models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        # Cleaned up the duplicate description string here:
        fields = ["title", "description", "status", "priority", "assigned_to", "client", "due_date"]
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        
        # 1. Extract the current user passed from get_form_kwargs()
        user = kwargs.pop('user', None)
        
        # 2. Run the core Django form initialization
        super().__init__(*args, **kwargs)

        # 3. Dynamic Dropdown filtering based on User Permissions & Active Statuses
        if "assigned_to" in self.fields and user:
            if not user.is_staff and not user.is_superuser:
                # Normal user: Lock dropdown down to ONLY their own profile record
                self.fields["assigned_to"].queryset = User.objects.filter(id=user.id)
                self.fields["assigned_to"].initial = user
                self.fields["assigned_to"].empty_label = None  # Remove blank spacer choice
            else:
                # Admin/Staff: Let them view all actual team members (exclude other admins)
                self.fields["assigned_to"].queryset = User.objects.filter(
                    is_superuser=False, 
                    is_staff=False
                )
                self.fields["assigned_to"].empty_label = "Assign to a team member..."
        
        # ✅ NEW FIX: Filter out any deactivated clients from the selection dropdown
        if "client" in self.fields:
            self.fields["client"].queryset = Client.objects.filter(is_active=True)
            self.fields["client"].empty_label = "Select an active client..."
        
        # 4. Prevent selecting previous calendar dates
        # today_str = timezone.now().date().strftime('%Y-%m-%d')
        # if "due_date" in self.fields:
        #     self.fields["due_date"].widget.attrs.update({"min": today_str})
            
        # 5. Global CSS Layout Injector Loop
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.Select, forms.SelectMultiple)):
                field.widget.attrs.update({"class": "form-select"})
            else:
                field.widget.attrs.update({"class": "form-control"})