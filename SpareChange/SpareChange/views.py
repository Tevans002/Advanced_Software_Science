from django.views.generic import TemplateView, CreateView
from django.db import IntegrityError

# from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from jobs.models import JobPost
from users.forms import BaseUserCreationForm


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["jobs"] = (
            JobPost.objects.select_related("location_proxy")
            .filter(hide_from_listings=False)
            .order_by("-created_at")
        )
        return context


class SignUpView(CreateView):
    form_class = BaseUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except IntegrityError as exc:
            # Convert DB uniqueness failures into a normal field error.
            if "users_base_user.username" in str(exc):
                form.add_error("username", "This username is already taken.")
                return self.form_invalid(form)
            raise
