from django import forms
from .models import JobPost
from django.core.exceptions import ValidationError
from datetime import date

class JobPostForm(forms.ModelForm):
    class Meta:
        model = JobPost
        exclude = ["poster", "created_at", "updated_at", "hide_from_listings"]
        widgets = {
            "start_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),
            "end_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),
        }
    # HERE IS THE VALIDATION LOGIC FOR USER FRIENDLY ERROR MESSAGES
    def clean_pay(self):
        """Validate the pay field"""
        pay = self.cleaned_data.get('pay')
        price_type = self.cleaned_data.get('price_type')

        # If price_type isn't set yet, skip validation for now
        if price_type is None:
            return pay

        # For negotiable jobs, pay is optional
        if price_type == 'NG':
            # Pay can be None or positive, but not negative
            if pay is not None and pay <= 0:
                raise ValidationError('Pay amount must be greater than zero.')
            return pay
        
        # For non-negotiable jobs, (FL or HR), pay is required
        if price_type in ['FL', 'HR']:
            if pay is None:
                raise ValidationError('Pay amount is required for Flate Rate and Hourly jobs.')
            
            if pay <= 0:
                raise ValidationError('Pay amount must be greater than zero.')
            
            return pay
        
        # Check if pay is too high
        if pay and pay > 999999.99:
            raise ValidationError('Pay amount is too high. Please enter valid amount.')
        
        return pay
    
    # HERE IS THE DATE VALIDATION
    def clean_start_date(self):
        """Validate start date is not in the past"""
        start_date = self.cleaned_data.get('start_date')

        # Require start date
        if not start_date:
            raise ValidationError('Start date is required.')

        # Check if date is in the past (using today's date as allowed)
        if start_date and start_date < date.today():
            raise ValidationError('Start date cannot be in the past. Please select today or a future date.')
        
        return start_date
    
    def clean_end_date(self):
        """Validate end date is not in the past"""
        end_date = self.cleaned_data.get('end_date')

        if end_date and end_date < date.today():
            raise ValidationError('End date cannot be in the past.')
        
        return end_date
    
    def clean(self):
        """Cross-field validation"""
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        # Validate dates
        if start_date and end_date and start_date > end_date:
            raise ValidationError({
                'end_date': 'End date must be after start date.'
            })
        
        return cleaned_data


