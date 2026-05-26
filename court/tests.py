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


class OpinionCreateViewTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            password="testpass123"
        )

    def test_create_requires_login(self):
        response = self.client.get(reverse("opinion-create"))
        self.assertRedirects(
            response,
            "/accounts/login/?next=/opinions/create/"
        )

    def test_create_opinion(self):
        self.client.login(
            username="testuser",
            password="testpass123"
        )
        response = self.client.post(reverse("opinion-create"), {
            "statement": "My new opinion",
            "tags": "coding, django"
        })
        self.assertRedirects(
            response,
            reverse("opinion-list")
        )
        self.assertTrue(Opinion.objects.filter(statement="My new opinion").exists())

    def test_create_sets_author(self):
        self.client.login(
            username="testuser",
            password="testpass123"
        )
        self.client.post(reverse("opinion-create"), {
            "statement": "My new opinion",
            "tags": ""
        })
        opinion = Opinion.objects.get(statement="My new opinion")
        self.assertEqual(opinion.author, self.user)


class OpinionUpdateViewTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.other = CustomUser.objects.create_user(
            username="other",
            password="pass123"
        )
        self.opinion = Opinion.objects.create(
            author=self.user,
            statement="Original statement"
        )

    def test_author_can_edit(self):
        self.client.login(
            username="testuser",
            password="testpass123"
        )
        response = self.client.post(
            reverse("opinion-update", kwargs={"pk": self.opinion.pk}),
            {"statement": "Updated statement", "tags": ""}
        )
        self.opinion.refresh_from_db()
        self.assertEqual(
            self.opinion.statement,
            "Updated statement"
        )

    def test_non_author_cannot_edit(self):
        self.client.login(
            username="other",
            password="pass123"
        )
        response = self.client.post(
            reverse("opinion-update", kwargs={"pk": self.opinion.pk}),
            {"statement": "Hacked!", "tags": ""}
        )
        self.opinion.refresh_from_db()
        self.assertNotEqual(
            self.opinion.statement,
            "Hacked!"
        )


class OpinionDeleteViewTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.other = CustomUser.objects.create_user(
            username="other",
            password="pass123"
        )
        self.opinion = Opinion.objects.create(
            author=self.user,
            statement="To be deleted"
        )

    def test_author_can_delete(self):
        self.client.login(
            username="testuser",
            password="testpass123"
        )
        self.client.post(
            reverse("opinion-delete",
                kwargs={"pk": self.opinion.pk})
        )
        self.assertFalse(Opinion.objects.filter(pk=self.opinion.pk).exists())

    def test_non_author_cannot_delete(self):
        self.client.login(
            username="other",
            password="pass123"
        )
        self.client.post(
            reverse("opinion-delete",
                    kwargs={"pk": self.opinion.pk})
        )
        self.assertTrue(Opinion.objects.filter(pk=self.opinion.pk).exists())


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
        self.client.login(
            username="other",
            password="pass123"
        )
        response = self.client.post(
            reverse("argument-create", kwargs={"pk": self.opinion.pk}),
            {"side": "DEF", "content": "I defend this"}
        )
        self.assertTrue(
            Argument.objects.filter(
            opinion=self.opinion,
            author=self.other).exists()
        )

    def test_author_cannot_argue_own_opinion(self):
        self.client.login(
            username="author",
            password="pass123"
        )
        self.client.post(
            reverse("argument-create", kwargs={"pk": self.opinion.pk}),
            {"side": "DEF", "content": "I defend myself"}
        )
        self.assertFalse(Argument.objects.filter(
            opinion=self.opinion,
            author=self.author
        ).exists())

    def test_cannot_argue_twice(self):
        self.client.login(
            username="other",
            password="pass123"
        )
        self.client.post(
            reverse("argument-create", kwargs={"pk": self.opinion.pk}),
            {"side": "DEF", "content": "First argument"}
        )
        self.client.post(
            reverse("argument-create", kwargs={"pk": self.opinion.pk}),
            {"side": "PRO", "content": "Second argument"}
        )
        self.assertEqual(
            Argument.objects.filter(
            opinion=self.opinion,
            author=self.other
            ).count(), 1
        )

    def test_cannot_argue_on_closed_opinion(self):
        self.opinion.closes_at = timezone.now() - timedelta(hours=1)
        self.opinion.save()
        self.client.login(
            username="other",
            password="pass123"
        )
        self.client.post(
            reverse("argument-create", kwargs={"pk": self.opinion.pk}),
            {"side": "DEF", "content": "Too late"}
        )
        self.assertFalse(
            Argument.objects.filter(
            opinion=self.opinion,
            author=self.other
            ).exists()
        )


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
        self.client.login(
            username="other",
            password="pass123"
        )
        self.client.post(
            reverse(
                "argument-delete",
                kwargs={"pk": self.argument.pk}
            )
        )
        self.assertFalse(
            Argument.objects.filter(
                pk=self.argument.pk
            ).exists()
        )

    def test_non_author_cannot_delete_argument(self):
        self.client.login(
            username="author",
            password="pass123"
        )
        self.client.post(
            reverse(
                "argument-delete",
                kwargs={"pk": self.argument.pk}
            )
        )
        self.assertTrue(
            Argument.objects.filter(
                pk=self.argument.pk
            ).exists()
        )


class ProfileViewTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            password="testpass123",
            bio="My bio"
        )

    def test_profile_requires_login(self):
        response = self.client.get(
            reverse(
                "profile",
                kwargs={"username": "testuser"}
            )
        )
        self.assertRedirects(
            response,
            "/accounts/login/?next=/profile/testuser/"
        )

    def test_profile_accessible_when_logged_in(self):
        self.client.login(
            username="testuser",
            password="testpass123"
        )
        response = self.client.get(
            reverse(
                "profile",
                kwargs={"username": "testuser"}
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_profile_shows_bio(self):
        self.client.login(
            username="testuser",
            password="testpass123"
        )
        response = self.client.get(
            reverse(
                "profile",
                kwargs={"username": "testuser"}
            )
        )
        self.assertContains(response, "My bio")


