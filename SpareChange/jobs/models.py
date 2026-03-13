from django.db import models
from users.models import base_user


class JobPost(models.Model):

    PRICE_TYPE_CHOICES = [
        ("FL", "Flat Rate"),
        ("HR", "Hourly"),
        ("NG", "Negotiable"),
    ]
    poster = models.ForeignKey(base_user, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    pay = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    price_type = models.CharField(
        max_length=2, choices=PRICE_TYPE_CHOICES, default="FL"
    )
    estimated_hours = models.PositiveIntegerField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_recurring = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    hide_from_listings = models.BooleanField(default=False)

    def __str__(self):
        """Return the job title as the string representation"""
        return self.title