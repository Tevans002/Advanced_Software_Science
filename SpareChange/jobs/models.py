from django.db import models
from django.core.exceptions import ValidationError
from users.models import base_user
from datetime import date

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
    start_date = models.DateField(null=True, blank=False) # changed this field to be required blank=False
    end_date = models.DateField(null=True, blank=True)
    is_recurring = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    hide_from_listings = models.BooleanField(default=False)

    def __str__(self):
        """Return the job title as the string representation"""
        return self.title
    
    # HERE IS THE VALIDATION LOGIC ENSURES DATA INTEGRITY AT THE DATABASE LEVEL

    def clean(self):
        """Model-level validation"""
        super().clean()

        # validate pay is positive if provided
        if self.pay is not None and self.pay <= 0:
            raise ValidationError({
                'pay': 'Pay amount must be greater than zero.'
            })
        
        # Additional validation: pay is required for non-negotiable jobs
        if self.price_type != 'NG' and self.pay is None:
            raise ValidationError({
                'pay': 'Pay amount is requierd for Flat Rate and Hourly jobs.'
            })
        
        # Validate start date is required and not in the past
        if not self.start_date:
            raise ValidationError({
                'start_date': 'Start date is required.'
            })
        
        if self.start_date and self.start_date < date.today():
            raise ValidationError({
                'start_date': 'Start date cannot be in the past. Please select today or a future date.'
            })
        
        # Validate end date is not in the past
        if self.end_date and self.end_date < date.today():
            raise ValidationError({
                'end_date': 'End date cannot be in the past.'
            })

        # Validate dates
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError({
                'end_date': 'End date must be after start date.'
            })