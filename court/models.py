from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta


class CustomUser(AbstractUser):
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.username

    @property
    def contrarian_score(self):
        return self.opinions.filter(verdict="defended").count()


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Opinion(models.Model):
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="opinions"
    )
    statement = models.CharField(max_length=200)
    tags = models.ManyToManyField(Tag, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    closes_at = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.closes_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)

    @property
    def is_open(self):
        return timezone.now() < self.closes_at

    @property
    def defend_count(self):
        return self.arguments.filter(side="DEF").count()

    @property
    def prosecute_count(self):
        return self.arguments.filter(side="PRO").count()

    @property
    def verdict(self):
        if self.is_open:
            return "ongoing"
        if self.defend_count > self.prosecute_count:
            return "defended"
        if self.prosecute_count > self.defend_count:
            return "prosecuted"
        return "hung jury"

    def __str__(self):
        return self.statement


class Argument(models.Model):
    SIDE_CHOICES = [("DEF", "Defend"), ("PRO", "Prosecute")]

    opinion = models.ForeignKey(
        Opinion, on_delete=models.CASCADE, related_name="arguments"
    )
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="arguments"
    )
    side = models.CharField(max_length=3, choices=SIDE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("opinion", "author")

    def __str__(self):
        return f"{self.author} - {self.get_side_display()} - {self.opinion}"
