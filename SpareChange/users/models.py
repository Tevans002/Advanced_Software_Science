from django.db import models
from django.contrib.auth.models import AbstractUser


class base_user(AbstractUser):
    user_bio = models.TextField(blank=True)
    zipcode = models.CharField(max_length=10, blank=True)
    profile_pic = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    @property
    def base_user(self):
        return self

    @property
    def user_id(self):
        return self.id

    def __str__(self):
        return self.username
