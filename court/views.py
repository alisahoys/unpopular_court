from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from .models import CustomUser, Opinion, Argument, Tag
from .forms import RegisterForm, OpinionForm, ArgumentForm, TagForm


class RegisterView(FormView):
    template_name = "court/register.html"
    form_class = RegisterForm
    success_url = reverse_lazy("login") #redirect path to login page after registration

    def form_valid(self, form): #calls automatically when the form passes validation
        form.save()
        messages.success(self.request, "Welcome to the court! Please login.")
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
        context["ongoing_count"] = Opinion.objects.filter(
            closes_at__gt=timezone.now()
        ).count()
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
        opinion.author = self.request.user #set author before saving to database
        opinion.save()

        tags_input = form.cleaned_data.get("tags", "") #tags field from OpinionForm
        if tags_input:
            tag_names = [t.strip() for t in tags_input.split(",")]
            for tag_name in tag_names:
                if tag_name:
                    tag, created = Tag.objects.get_or_create(name=tag_name) # created - True if created, False if already exists
                    opinion.tags.add(tag) #attach it to this opinion (we do not use created anywhere - django just requires it

        messages.success(self.request, "Your opinion is now on trial! ⚖️")
        return redirect(self.success_url)


class OpinionUpdateView(LoginRequiredMixin, UpdateView):
    model = Opinion
    template_name = "court/opinion_form.html"
    form_class = OpinionForm

    def get_success_url(self):
        return reverse_lazy("opinion-detail", kwargs={"pk": self.object.pk}) # after editing we redirect back to that specific opinion's detail page.

    def get_queryset(self):
        return Opinion.objects.filter(author=self.request.user) #It only allows editing opinions that belong to the logged in user.

    def get_initial(self):
        initial = super().get_initial()
        opinion = self.get_object()
        initial["tags"] = ", ".join([tag.name for tag in opinion.tags.all()]) # pre-fills the tags textarea with existing tags when editing.
        return initial

    def form_valid(self, form):
        opinion = form.save(commit=False)
        opinion.save()

        opinion.tags.clear() # erases tags from database so existing tags won't be added again
        tags_input = form.cleaned_data.get("tags", "")
        if tags_input:
            tag_names = [t.strip() for t in tags_input.split(",")]
            for tag_name in tag_names:
                if tag_name:
                    tag, created = Tag.objects.get_or_create(name=tag_name)
                    opinion.tags.add(tag)

        messages.success(self.request, "Opinion updated! ✏️")
        return redirect(self.get_success_url())


class OpinionDeleteView(LoginRequiredMixin, DeleteView):
    model = Opinion
    template_name = "court/opinion_confirm_delete.html"
    success_url = reverse_lazy("opinion-list")

    def get_queryset(self):
        return Opinion.objects.filter(author=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Opinion dismissed from the court. 🗑️")
        return super().delete(request, *args, **kwargs)


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
        messages.success(self.request, "Your argument has been filed! ⚖️")
        return redirect("opinion-detail", pk=opinion.pk)


class ArgumentDeleteView(LoginRequiredMixin, DeleteView):
    model = Argument
    template_name = "court/argument_confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy("opinion-detail", kwargs={"pk": self.object.opinion.pk})

    def get_queryset(self):
        return Argument.objects.filter(author=self.request.user) #returns only arguments that belong to the logged in user. Then Django takes that list and looks for the specific one from the URL

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Argument withdrawn. 🏳️")
        return super().delete(request, *args, **kwargs)


class TagListView(ListView):
    model = Tag
    template_name = "court/tag_list.html"
    context_object_name = "tags"


class TagCreateView(LoginRequiredMixin, CreateView):
    model = Tag
    form_class = TagForm
    template_name = "court/tag_form.html"
    success_url = reverse_lazy("tag-list")

    def form_valid(self, form):
        messages.success(self.request, "New tag added to the court records! 🏷️")
        return super().form_valid(form)


class ProfileView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = "court/profile.html"
    context_object_name = "profile_user"
    slug_field = "username" # look up CustomUser by username instead of pk in database: CustomUser.objects.get(username=...)
    slug_url_kwarg = "username" # tells Django the URL parameter is called username

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_user = self.object

        opinions = Opinion.objects.filter(author=profile_user)
        context["opinions"] = opinions
        context["total_opinions"] = opinions.count()
        context["total_arguments"] = Argument.objects.filter(author=profile_user).count()

        defended = sum(1 for o in opinions if o.verdict == "defended")
        context["contrarian_score"] = defended

        return context