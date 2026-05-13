from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from apps.users.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for the custom User model."""

    ordering = ["email"]
    list_display = ["email", "name", "date_of_birth", "is_active", "is_staff", "created_date"]
    list_filter = ["is_active", "is_staff", "is_superuser"]
    search_fields = ["email", "name"]
    readonly_fields = ["id", "created_date", "modified_date"]

    fieldsets = (
        (None, {"fields": ("id", "email", "password")}),
        ("Personal Info", {"fields": ("name", "date_of_birth")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Timestamps", {"fields": ("created_date", "modified_date")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "name", "date_of_birth", "password1", "password2"),
            },
        ),
    )
