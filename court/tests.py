from django.test import TestCase
from django.utils import timezone

from datetime import timedelta

from court.models import CustomUser, Opinion, Argument


class CustomUserModelTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.opinion = Opinion.objects.create(
            author=self.user,
            statement="Test opinion"
        )

    def test_contrarian_score_zero_by_default(self):
        self.assertEqual(self.user.contrarian_score, 0)

    def test_contrarian_score_counts_defended(self):
        # close the opinion and make defend win
        self.opinion.closes_at = timezone.now() - timedelta(hours=1)
        self.opinion.save()
        other_user = CustomUser.objects.create_user(
            username="other",
            password="pass123"
        )
        Argument.objects.create(
            opinion=self.opinion,
            author=other_user,
            side="DEF",
            content="I defend this"
        )
        self.assertEqual(self.user.contrarian_score, 1)
