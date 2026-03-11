# users/forms.py
from django.contrib.auth.forms import UserCreationForm
from users.models import base_user


class BaseUserCreationForm(UserCreationForm):
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
