from django import forms
from .models import JobPost


class JobPostForm(forms.ModelForm):
    class Meta:
        model = JobPost
        exclude = ["poster", "created_at", "updated_at", "hide_from_listings"]
