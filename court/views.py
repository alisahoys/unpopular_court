from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from .models import CustomUser, Opinion, Argument, Tag
from .forms import RegisterForm, OpinionForm, ArgumentForm, TagForm


class RegisterView(FormView):
    template_name = "court/register.html"
    form_class = RegisterForm
    success_url = reverse_lazy("login") #redirect path to login page after registration

    def form_valid(self, form): #calls automatically when the form passes validation
        form.save()
        return super().form_valid(form) #does the redirect to success_url automatically.