# users/forms.py
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from users.models import base_user


class BaseUserCreationForm(UserCreationForm):
    def clean_username(self):
        username = self.cleaned_data.get("username", "")
        if base_user.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken.")
        return username

    class Meta(UserCreationForm.Meta):
        model = base_user
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
            "user_bio",
            "zipcode",
            "profile_pic",
            "date_of_birth",
        )
