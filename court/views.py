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
