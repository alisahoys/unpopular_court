from django import forms
from .models import Opinion, Argument, Tag
from allauth.account.forms import SignupForm


class CustomSignupForm(SignupForm):
    bio = forms.CharField(widget=forms.Textarea, required=False)

    def save(self, request):
        user = super().save(request)
        user.bio = self.cleaned_data.get("bio", "")
        user.save()
        return user


class OpinionForm(forms.ModelForm):
    tags = forms.CharField(
        max_length=200,
        required=False,
        help_text="Enter tags separated by commas e.g. coding, hot takes",
        widget=forms.Textarea(attrs={"rows": 2})
    )

    class Meta:
        model = Opinion
        fields = ("statement", "tags")


class ArgumentForm(forms.ModelForm):
    class Meta:
        model = Argument
        fields = ("side", "content")


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ("name",)
