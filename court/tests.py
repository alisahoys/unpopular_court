from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from datetime import timedelta

from court.models import CustomUser, Opinion, Argument, Tag


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


class OpinionModelTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            password="testpass123"
        )

    def test_closes_at_set_automatically(self):
        opinion = Opinion.objects.create(
            author=self.user,
            statement="Test opinion"
        )
        self.assertIsNotNone(opinion.closes_at)

    def test_closes_at_not_overwritten_on_update(self):
        opinion = Opinion.objects.create(
            author=self.user,
            statement="Test opinion"
        )
        original_closes_at = opinion.closes_at
        opinion.statement = "Updated statement"
        opinion.save()
        self.assertEqual(opinion.closes_at, original_closes_at)

    def test_is_open_true_for_new_opinion(self):
        opinion = Opinion.objects.create(
            author=self.user,
            statement="Test opinion"
        )
        self.assertTrue(opinion.is_open)

    def test_is_open_false_for_expired_opinion(self):
        opinion = Opinion.objects.create(
            author=self.user,
            statement="Test opinion"
        )
        opinion.closes_at = timezone.now() - timedelta(hours=1)
        opinion.save()
        self.assertFalse(opinion.is_open)

    def test_verdict_ongoing_when_open(self):
        opinion = Opinion.objects.create(
            author=self.user,
            statement="Test opinion"
        )
        self.assertEqual(opinion.verdict, "ongoing")

    def test_verdict_defended(self):
        opinion = Opinion.objects.create(
            author=self.user,
            statement="Test opinion"
        )
        opinion.closes_at = timezone.now() - timedelta(hours=1)
        opinion.save()
        other1 = CustomUser.objects.create_user(
            username="u1",
            password="pass123"
        )
        other2 = CustomUser.objects.create_user(
            username="u2",
            password="pass123"
        )
        Argument.objects.create(
            opinion=opinion,
            author=other1, side="DEF",
            content="defend"
        )
        Argument.objects.create(
            opinion=opinion,
            author=other2,
            side="DEF",
            content="defend2"
        )
        self.assertEqual(opinion.verdict, "defended")

    def test_verdict_prosecuted(self):
        opinion = Opinion.objects.create(
            author=self.user,
            statement="Test opinion"
        )
        opinion.closes_at = timezone.now() - timedelta(hours=1)
        opinion.save()
        other1 = CustomUser.objects.create_user(
            username="u1",
            password="pass123"
        )
        other2 = CustomUser.objects.create_user(
            username="u2",
            password="pass123"
        )
        Argument.objects.create(
            opinion=opinion,
            author=other1,
            side="PRO",
            content="prosecute"
        )
        Argument.objects.create(
            opinion=opinion,
            author=other2,
            side="PRO",
            content="prosecute2"
        )
        self.assertEqual(opinion.verdict, "prosecuted")

    def test_verdict_hung_jury(self):
        opinion = Opinion.objects.create(
            author=self.user,
            statement="Test opinion"
        )
        opinion.closes_at = timezone.now() - timedelta(hours=1)
        opinion.save()
        other1 = CustomUser.objects.create_user(
            username="u1",
            password="pass123"
        )
        other2 = CustomUser.objects.create_user(
            username="u2",
            password="pass123"
        )
        Argument.objects.create(
            opinion=opinion,
            author=other1,
            side="DEF",
            content="defend"
        )
        Argument.objects.create(
            opinion=opinion,
            author=other2,
            side="PRO",
            content="prosecute"
        )
        self.assertEqual(opinion.verdict, "hung jury")

    def test_defend_count(self):
        opinion = Opinion.objects.create(
            author=self.user,
            statement="Test"
        )
        other = CustomUser.objects.create_user(
            username="other",
            password="pass123"
        )
        Argument.objects.create(
            opinion=opinion,
            author=other,
            side="DEF",
            content="defend"
        )
        self.assertEqual(opinion.defend_count, 1)

    def test_prosecute_count(self):
        opinion = Opinion.objects.create(
            author=self.user,
            statement="Test"
        )
        other = CustomUser.objects.create_user(
            username="other",
            password="pass123"
        )
        Argument.objects.create(
            opinion=opinion,
            author=other,
            side="PRO",
            content="prosecute"
        )
        self.assertEqual(opinion.prosecute_count, 1)


class OpinionListViewTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.opinion = Opinion.objects.create(
            author=self.user,
            statement="Test opinion"
        )

    def test_opinion_list_accessible(self):
        response = self.client.get(reverse("opinion-list"))
        self.assertEqual(response.status_code, 200)

    def test_opinion_list_search(self):
        response = self.client.get(reverse("opinion-list") + "?search=Test")
        self.assertContains(response, "Test opinion")

    def test_opinion_list_search_no_results(self):
        response = self.client.get(
            reverse("opinion-list") + "?search=zzznomatch"
        )
        self.assertNotContains(response, "Test opinion")

    def test_opinion_list_filter_by_tag(self):
        tag = Tag.objects.create(name="coding")
        self.opinion.tags.add(tag)
        response = self.client.get(reverse("opinion-list") + "?tag=coding")
        self.assertContains(response, "Test opinion")

    def test_opinion_list_search_by_tag_name(self):
        tag = Tag.objects.create(name="philosophy")
        self.opinion.tags.add(tag)
        response = self.client.get(reverse("opinion-list") + "?search=philosophy")
        self.assertContains(response, "Test opinion")


class OpinionDetailViewTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.opinion = Opinion.objects.create(
            author=self.user,
            statement="Test opinion"
        )

    def test_detail_requires_login(self):
        response = self.client.get(
            reverse("opinion-detail",
                    kwargs={"pk": self.opinion.pk})
        )
        self.assertRedirects(
            response,
            f"/accounts/login/?next=/opinions/{self.opinion.pk}/"
        )

    def test_detail_accessible_when_logged_in(self):
        self.client.login(
            username="testuser",
            password="testpass123"
        )
        response = self.client.get(
            reverse("opinion-detail",
                    kwargs={"pk": self.opinion.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_author_sees_edit_delete_buttons(self):
        self.client.login(
            username="testuser",
            password="testpass123"
        )
        response = self.client.get(
            reverse("opinion-detail",
                    kwargs={"pk": self.opinion.pk})
        )
        self.assertContains(
            response, "EDIT OPINION"
        )
        self.assertContains(
            response, "DELETE OPINION"
        )

    def test_non_author_does_not_see_edit_delete(self):
        other = CustomUser.objects.create_user(
            username="other",
            password="pass123"
        )
        self.client.login(
            username="other",
            password="pass123"
        )
        response = self.client.get(
            reverse("opinion-detail",
                    kwargs={"pk": self.opinion.pk})
        )
        self.assertNotContains(
            response,
            "EDIT OPINION"
        )
        self.assertNotContains(
            response,
            "DELETE OPINION"
        )
