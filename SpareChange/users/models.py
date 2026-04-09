from django.db import models
from django.contrib.auth.models import AbstractUser


class base_user(AbstractUser):
    user_bio = models.TextField(blank=True)
    zipcode = models.CharField(max_length=10, blank=True)
    profile_pic = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    # location proxy
    location_proxy = models.OneToOneField(
        "location.Location",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user",
    )

    def save(self, *args, **kwargs):
        from location.models import Location

        is_new = self._state.adding
        old_zipcode = None

        if not is_new:
            old_zipcode = (
                base_user.objects.filter(pk=self.pk)
                .values_list("zipcode", flat=True)
                .first()
            )

        super().save(*args, **kwargs)

        if self.zipcode:
            if is_new and not self.location_proxy_id:
                self.location_proxy = Location.create_for_user(self.zipcode)
                super().save(update_fields=["location_proxy"])
            elif not is_new and self.zipcode != old_zipcode:
                if self.location_proxy:
                    self.location_proxy.update_from_zip(self.zipcode)
                else:
                    self.location_proxy = Location.create_for_user(self.zipcode)
                    super().save(update_fields=["location_proxy"])

    def __str__(self):
        return self.username

    @property
    def base_user(self):
        return self

    @property
    def user_id(self):
        return self.id
