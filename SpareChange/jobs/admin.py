from django.contrib import admin
from .models import JobPost


@admin.register(JobPost)
class JobPostAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "title",
        "poster",
        "location",
        "pay",
        "price_type",
        "start_date",
        "hide_from_listings",
    ]
    list_filter = ["price_type", "is_recurring", "hide_from_listings"]
    search_fields = ["title", "description", "location", "poster__username"]
    ordering = ["-created_at"]
