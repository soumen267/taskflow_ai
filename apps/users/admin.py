from django.contrib import admin
from apps.accounts.models import User  # ADD THIS INSTEAD

# Unregister the default User admin first so Django doesn't complain about a duplicate registration
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # 'username', 'first_name', 'last_name', and 'date_joined' are the correct built-in fields
    list_display = ("username", "first_name", "last_name", "email", "is_staff", "avatar", "date_joined")
    search_fields = ("username", "first_name", "last_name", "email")
    date_hierarchy = "date_joined"  # Changed from 'created_at' to 'date_joined'