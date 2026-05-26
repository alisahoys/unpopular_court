from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Opinion, Argument, Tag


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Extra", {"fields": ("bio",)}),
    )


@admin.register(Opinion)
class OpinionAdmin(admin.ModelAdmin):
    list_display = ("statement", "author", "created_at", "closes_at")
    list_filter = ("created_at",)
    search_fields = ("statement",)
    filter_horizontal = ("tags",)


@admin.register(Argument)
class ArgumentAdmin(admin.ModelAdmin):
    list_display = ("author", "side", "opinion", "created_at")
    list_filter = ("side",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)