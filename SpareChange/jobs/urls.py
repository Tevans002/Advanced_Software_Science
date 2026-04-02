from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.create_job, name="create_job"),
    path("<int:job_id>/confirm/", views.confirm_job, name="confirm_job"),
]
