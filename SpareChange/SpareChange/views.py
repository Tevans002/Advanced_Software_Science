from django.views.generic import TemplateView, CreateView

# from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from users.forms import BaseUserCreationForm


class HomeView(TemplateView):
    template_name = "home.html"


class SignUpView(CreateView):
    form_class = BaseUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"
