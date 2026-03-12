from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import base_user


@admin.register(base_user)
class BaseUserAdmin(UserAdmin):
    list_display = [
        "id",
        "username",
        "email",
        "first_name",
        "last_name",
        "is_verified",
        "is_staff",
        "date_joined",
    ]
    list_filter = ["is_verified", "is_staff", "is_superuser", "is_active"]
    search_fields = ["username", "email", "first_name", "last_name", "zipcode"]
    ordering = ["-date_joined"]

    # Add your custom fields to the edit page
    fieldsets = UserAdmin.fieldsets + (
        (
            "Profile",
            {
                "fields": (
                    "user_bio",
                    "zipcode",
                    "profile_pic",
                    "date_of_birth",
                    "is_verified",
                )
            },
        ),
    )

    # Add your custom fields to the create user page
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Profile",
            {
                "fields": (
                    "user_bio",
                    "zipcode",
                    "profile_pic",
                    "date_of_birth",
                    "is_verified",
                )
            },
        ),
    )
