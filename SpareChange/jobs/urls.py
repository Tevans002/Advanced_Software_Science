from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.create_job, name="create_job"),
    path("delete/<int:job_id>/", views.delete_job, name="delete_job"),

    path('enhance-description/', views.enhance_description, name='enhance_description'),
]
