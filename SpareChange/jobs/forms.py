from django import forms
from .models import JobPost


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
