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


class OpinionListView(ListView): #the home page logic
    model = Opinion
    template_name = "court/opinion_list.html"
    context_object_name = "opinions"

    def get_queryset(self):
        queryset = Opinion.objects.all().order_by("-created_at")
        search = self.request.GET.get("search")
        tag = self.request.GET.get("tag")

        if search:
            queryset = queryset.filter(statement__icontains=search)
        if tag:
            queryset = queryset.filter(tags__name=tag)

        return queryset

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["tags"] = Tag.objects.all()
        ctx["search"] = self.request.GET.get("search", "")
        ctx["selected_tag"] = self.request.GET.get("tag", "")
        return ctx