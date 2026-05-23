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
    context_object_name = "opinions" #pass them to the template under the name 'opinions': context["opinions"] = Opinion.objects.all()

    def get_queryset(self): #which options to show
        queryset = Opinion.objects.all().order_by("-created_at")
        search = self.request.GET.get("search") # a search word after ? in url
        tag = self.request.GET.get("tag")

        if search:
            queryset = queryset.filter(statement__icontains=search)
        if tag:
            queryset = queryset.filter(tags__name=tag)

        return queryset

    def get_context_data(self, **kwargs): # what else to pass to the template
        context = super().get_context_data(**kwargs) #opinions are here
        context["tags"] = Tag.objects.all()
        context["search"] = self.request.GET.get("search", "")
        context["selected_tag"] = self.request.GET.get("tag", "")
        return context


class OpinionDetailView(LoginRequiredMixin, DetailView):
    model = Opinion
    template_name = "court/opinion_detail.html"
    context_object_name = "opinion"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        opinion = self.object #self is OpinionDetailView instance, opinion instance - is it's object
        user = self.request.user # the person viewing the opinion

        context["has_argued"] = Argument.objects.filter(
            opinion=opinion,
            author=user
        ).exists() #if user already have an Argument for this opinion - True

        context["arguments"] = Argument.objects.filter(
            opinion=opinion
        ).order_by("-created_at")

        context["is_author"] = opinion.author == user # to show edit/delete buttons only to the author
        context["argument_form"] = ArgumentForm() # i want to have an argument form on the same page as an opinion

        return context


class OpinionCreateView(LoginRequiredMixin, CreateView):
    model = Opinion
    template_name = "court/opinion_form.html"
    form_class = OpinionForm
    success_url = reverse_lazy("opinion-list")

    def form_valid(self, form):
        opinion = form.save(commit=False) # saves the form data with the opinion but doesn't write to database yet - to handle author and tags first.
        opinion.author = self.request.user #we can't set an author without form.save before.
        opinion.save()

        tags_input = form.cleaned_data.get("tags", "") #tags field from OpinionForm
        if tags_input:
            tag_names = [t.strip() for t in tags_input.split(",")]
            for tag_name in tag_names:
                if tag_name:
                    tag, created = Tag.objects.get_or_create(name=tag_name) # created - True if created, False if already exists
                    opinion.tags.add(tag) #attach it to this opinion (we do not use created anywhere - django just requires it

        return redirect(self.success_url)


class OpinionUpdateView(LoginRequiredMixin, UpdateView):
    model = Opinion
    template_name = "court/opinion_form.html"
    form_class = OpinionForm

    def get_success_url(self):
        return reverse_lazy("opinion-detail", kwargs={"pk": self.object.pk}) # after editing we redirect back to that specific opinion's detail page.

    def get_queryset(self):
        return Opinion.objects.filter(author=self.request.user) #It only allows editing opinions that belong to the logged in user.


class OpinionDeleteView(LoginRequiredMixin, DeleteView):
    model = Opinion
    template_name = "court/opinion_confirm_delete.html"
    success_url = reverse_lazy("opinion-list")

    def get_queryset(self):
        return Opinion.objects.filter(author=self.request.user)


class ArgumentCreateView(LoginRequiredMixin, CreateView):
    model = Argument
    form_class = ArgumentForm
    template_name = "court/opinion_detail.html"

    def dispatch(self, request, *args, **kwargs):
        opinion = get_object_or_404(Opinion, pk=self.kwargs["pk"]) #fetches the Opinion by pk from the URL, returns 404 if it doesn't exist. self.kwargs["pk"] gets the pk number from the URL. So /opinions/5/argue/ gives us self.kwargs["pk"] = 5.

        if opinion.author == request.user:
            return redirect("opinion-detail", pk=opinion.pk) #Can't argue for own opinion!

        if not opinion.is_open:
            return redirect("opinion-detail", pk=opinion.pk)

        if Argument.objects.filter(opinion=opinion, author=request.user).exists(): #redirect back if already argued
            return redirect("opinion-detail", pk=opinion.pk)

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        opinion = get_object_or_404(Opinion, pk=self.kwargs["pk"])
        argument = form.save(commit=False)
        argument.author = self.request.user
        argument.opinion = opinion #arguments store the opinion ID not the other way around
        argument.save()
        return redirect("opinion-detail", pk=opinion.pk)


class ArgumentDeleteView(LoginRequiredMixin, DeleteView):
    model = Argument
    template_name = "court/argument_confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy("opinion-detail", kwargs={"pk": self.object.opinion.pk})

    def get_queryset(self):
        return Argument.objects.filter(author=self.request.user)