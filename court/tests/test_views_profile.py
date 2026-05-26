from django.test import TestCase
from django.urls import reverse

from court.models import CustomUser


class ProfileViewTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            password="testpass123",
            bio="My bio"
        )

    def test_profile_requires_login(self):
        response = self.client.get(
            reverse("profile", kwargs={"username": "testuser"})
        )
        self.assertRedirects(
            response,
            reverse("account_login") + "?next=/profile/testuser/"
        )

    def test_profile_accessible_when_logged_in(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(
            reverse("profile", kwargs={"username": "testuser"})
        )
        self.assertEqual(response.status_code, 200)

    def test_profile_shows_bio(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(
            reverse("profile", kwargs={"username": "testuser"})
        )
        self.assertContains(response, "My bio")
