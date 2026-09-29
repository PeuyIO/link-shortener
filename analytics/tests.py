from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from links.models import Link
from analytics.models import Click


User = get_user_model()


class ClickModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="analytics_test_user",
            password="StrongPassword123!",
        )

        self.link = Link.objects.create(
            owner=self.user,
            short_code="analytics1",
            original_url="https://example.com",
        )

    def test_create_click(self):
        """Переход создаётся и привязывается к ссылке."""
        click = Click.objects.create(link=self.link)

        self.assertEqual(click.link, self.link)
        self.assertIsNotNone(click.pk)

    def test_click_has_timestamp(self):
        """У перехода фиксируется время создания."""
        click = Click.objects.create(link=self.link)

        self.assertIsNotNone(click.clicked_at)

    def test_multiple_clicks_belong_to_same_link(self):
        """Несколько переходов могут относиться к одной ссылке."""
        Click.objects.create(link=self.link)
        Click.objects.create(link=self.link)
        Click.objects.create(link=self.link)

        self.assertEqual(
            Click.objects.filter(link=self.link).count(),
            3,
        )

    def test_clicks_are_separated_by_link(self):
        """Переходы разных ссылок не смешиваются."""
        another_link = Link.objects.create(
            owner=self.user,
            short_code="analytics2",
            original_url="https://example.org",
        )

        Click.objects.create(link=self.link)
        Click.objects.create(link=self.link)
        Click.objects.create(link=another_link)

        self.assertEqual(
            Click.objects.filter(link=self.link).count(),
            2,
        )
        self.assertEqual(
            Click.objects.filter(link=another_link).count(),
            1,
        )
