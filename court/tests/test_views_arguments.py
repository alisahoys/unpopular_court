from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from court.models import CustomUser, Opinion, Argument


class ArgumentCreateViewTest(TestCase):

    def setUp(self):
        self.author = CustomUser.objects.create_user(
            username="author",
            password="pass123"
        )
        self.other = CustomUser.objects.create_user(
            username="other",
            password="pass123"
        )
        self.opinion = Opinion.objects.create(
            author=self.author,
            statement="Test opinion"
        )

    def test_user_can_argue(self):
        self.client.login(username="other", password="pass123")
        self.client.post(
            reverse("argument-create", kwargs={"pk": self.opinion.pk}),
            {"side": "DEF", "content": "I defend this"}
        )
        self.assertTrue(Argument.objects.filter(
            opinion=self.opinion,
            author=self.other
        ).exists())

    def test_author_cannot_argue_own_opinion(self):
        self.client.login(username="author", password="pass123")
        self.client.post(
            reverse("argument-create", kwargs={"pk": self.opinion.pk}),
            {"side": "DEF", "content": "I defend myself"}
        )
        self.assertFalse(Argument.objects.filter(
            opinion=self.opinion,
            author=self.author
        ).exists())

    def test_cannot_argue_twice(self):
        self.client.login(username="other", password="pass123")
        self.client.post(
            reverse("argument-create", kwargs={"pk": self.opinion.pk}),
            {"side": "DEF", "content": "First argument"}
        )
        self.client.post(
            reverse("argument-create", kwargs={"pk": self.opinion.pk}),
            {"side": "PRO", "content": "Second argument"}
        )
        self.assertEqual(Argument.objects.filter(
            opinion=self.opinion,
            author=self.other
        ).count(), 1)

    def test_cannot_argue_on_closed_opinion(self):
        self.opinion.closes_at = timezone.now() - timedelta(hours=1)
        self.opinion.save()
        self.client.login(username="other", password="pass123")
        self.client.post(
            reverse("argument-create", kwargs={"pk": self.opinion.pk}),
            {"side": "DEF", "content": "Too late"}
        )
        self.assertFalse(Argument.objects.filter(
            opinion=self.opinion,
            author=self.other
        ).exists())


class ArgumentDeleteViewTest(TestCase):

    def setUp(self):
        self.author = CustomUser.objects.create_user(
            username="author",
            password="pass123"
        )
        self.other = CustomUser.objects.create_user(
            username="other",
            password="pass123"
        )
        self.opinion = Opinion.objects.create(
            author=self.author,
            statement="Test opinion"
        )
        self.argument = Argument.objects.create(
            opinion=self.opinion,
            author=self.other,
            side="DEF",
            content="My argument"
        )

    def test_author_can_delete_argument(self):
        self.client.login(username="other", password="pass123")
        self.client.post(
            reverse("argument-delete", kwargs={"pk": self.argument.pk})
        )
        self.assertFalse(
            Argument.objects.filter(pk=self.argument.pk).exists()
        )

    def test_non_author_cannot_delete_argument(self):
        self.client.login(username="author", password="pass123")
        self.client.post(
            reverse("argument-delete", kwargs={"pk": self.argument.pk})
        )
        self.assertTrue(
            Argument.objects.filter(pk=self.argument.pk).exists()
        )
