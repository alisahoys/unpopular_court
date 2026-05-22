from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Opinion, Argument, Tag


class RegisterForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email", "password1", "password2") #UserCreationForm doesn't include email by default, so I list all the fields we need including the new one.


class OpinionForm(forms.ModelForm):
    tags = forms.CharField( #not in Meta because i want it as a separate customized field in the form (not a default ugly manytomany field)
        max_length=200,
        required=False,
        help_text="Enter tags separated by commas e.g. coding, hot takes" #helper text below the field
    )

    class Meta:
        model = Opinion
        fields = ("statement", "tags") #fields from the model are built automatically, so no need to override them (as I did with tags)


class ArgumentForm(forms.ModelForm):
    class Meta:
        model = Argument
        fields = ("side", "content")


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ("name",)