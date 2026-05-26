from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.db.models import Q
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from .models import CustomUser, Opinion, Argument, Tag
from .forms import OpinionForm, ArgumentForm, TagForm

class OpinionListView(ListView):
    model = Opinion
    template_name = "court/opinion_list.html"
    context_object_name = "opinions"

    def get_queryset(self):
        queryset = Opinion.objects.all().order_by("-created_at")
        search = self.request.GET.get("search")
        tag = self.request.GET.get("tag")

        if search:
            queryset = queryset.filter(
                Q(statement__icontains=search) | Q(tags__name__icontains=search)).distinct()
        if tag:
            queryset = queryset.filter(tags__name=tag)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
        opinion = self.object
        user = self.request.user

        context["has_argued"] = Argument.objects.filter(
            opinion=opinion,
            author=user
        ).exists()

        context["arguments"] = Argument.objects.filter(
            opinion=opinion
        ).order_by("-created_at")

        context["is_author"] = opinion.author == user
        context["argument_form"] = ArgumentForm()
        context["total_arguments"] = opinion.defend_count + opinion.prosecute_count

        return context


class OpinionCreateView(LoginRequiredMixin, CreateView):
    model = Opinion
    template_name = "court/opinion_form.html"
    form_class = OpinionForm
    success_url = reverse_lazy("opinion-list")

    def form_valid(self, form):
        opinion = form.save(commit=False)
        opinion.author = self.request.user
        opinion.save()

        tags_input = form.cleaned_data.get("tags", "")
        if tags_input:
            tag_names = [t.strip() for t in tags_input.split(",")]
            for tag_name in tag_names:
                if tag_name:
                    tag, created = Tag.objects.get_or_create(name=tag_name)
                    opinion.tags.add(tag)

        messages.success(self.request, "Your opinion is now on trial! ⚖️")
        return redirect(self.success_url)


class OpinionUpdateView(LoginRequiredMixin, UpdateView):
    model = Opinion
    template_name = "court/opinion_form.html"
    form_class = OpinionForm

    def get_success_url(self):
        return reverse_lazy("opinion-detail", kwargs={"pk": self.object.pk})

    def get_queryset(self):
        return Opinion.objects.filter(author=self.request.user)

    def get_initial(self):
        initial = super().get_initial()
        opinion = self.get_object()
        initial["tags"] = ", ".join([tag.name for tag in opinion.tags.all()])
        return initial

    def form_valid(self, form):
        opinion = form.save(commit=False)
        opinion.save()

        opinion.tags.clear()
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
        opinion = get_object_or_404(Opinion, pk=self.kwargs["pk"])
        if opinion.author == request.user:
            return redirect("opinion-detail", pk=opinion.pk)

        if not opinion.is_open:
            return redirect("opinion-detail", pk=opinion.pk)

        if Argument.objects.filter(opinion=opinion, author=request.user).exists():
            return redirect("opinion-detail", pk=opinion.pk)

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        opinion = get_object_or_404(Opinion, pk=self.kwargs["pk"])
        argument = form.save(commit=False)
        argument.author = self.request.user
        argument.opinion = opinion
        argument.save()
        messages.success(self.request, "Your argument has been filed! ⚖️")
        return redirect("opinion-detail", pk=opinion.pk)


class ArgumentDeleteView(LoginRequiredMixin, DeleteView):
    model = Argument
    template_name = "court/argument_confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy("opinion-detail", kwargs={"pk": self.object.opinion.pk})

    def get_queryset(self):
        return Argument.objects.filter(author=self.request.user)

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
    slug_field = "username"
    slug_url_kwarg = "username"

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