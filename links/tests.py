from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from .models import Link

from analytics.models import Click


User = get_user_model()


class LinkCRUDTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="link_test_user",
            email="link_test@example.com",
            password="StrongTestPassword123!",
        )

        self.other_user = User.objects.create_user(
            username="other_link_user",
            email="other_link@example.com",
            password="StrongTestPassword123!",
        )

        self.client.force_authenticate(user=self.user)

        self.list_url = reverse("link-list")

        self.link = Link.objects.create(
            owner=self.user,
            short_code="test123",
            original_url="https://example.com/",
        )

        self.other_link = Link.objects.create(
            owner=self.other_user,
            short_code="other123",
            original_url="https://google.com/",
        )

    def test_create_link(self):
        """Авторизованный пользователь может создать ссылку."""
        response = self.client.post(
            self.list_url,
            {"original_url": "https://github.com/"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(
            Link.objects.filter(
                owner=self.user,
                original_url="https://github.com/",
            ).exists()
        )

    def test_get_link_list(self):
        """Пользователь получает только свои ссылки."""
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        if isinstance(data, dict) and "results" in data:
            data = data["results"]

        link_ids = {item["id"] for item in data}

        self.assertIn(self.link.id, link_ids)
        self.assertNotIn(self.other_link.id, link_ids)

    def test_get_own_link(self):
        """Пользователь может получить свою ссылку."""
        response = self.client.get(
            reverse("link-detail", kwargs={"pk": self.link.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.link.id)
        self.assertEqual(
            response.data["original_url"],
            self.link.original_url,
        )

    def test_cannot_get_other_users_link(self):
        """Пользователь не может получить чужую ссылку."""
        response = self.client.get(
            reverse("link-detail", kwargs={"pk": self.other_link.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_own_link(self):
        """Пользователь может удалить свою ссылку."""
        response = self.client.delete(
            reverse("link-detail", kwargs={"pk": self.link.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Link.objects.filter(pk=self.link.pk).exists()
        )

    def test_cannot_delete_other_users_link(self):
        """Пользователь не может удалить чужую ссылку."""
        response = self.client.delete(
            reverse("link-detail", kwargs={"pk": self.other_link.pk})
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(
            Link.objects.filter(pk=self.other_link.pk).exists()
        )

    def test_create_link_without_authentication(self):
        """Создание ссылки без авторизации запрещено."""
        self.client.force_authenticate(user=None)

        response = self.client.post(
            self.list_url,
            {"original_url": "https://example.com/new"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
class LinkRedirectTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="redirect_test_user",
            email="redirect_test@example.com",
            password="StrongTestPassword123!",
        )

        self.link = Link.objects.create(
            owner=self.user,
            short_code="redir123",
            original_url="https://example.com/",
            is_active=True,
        )

        self.redirect_url = reverse(
            "link-redirect",
            kwargs={"short_code": self.link.short_code},
        )

    def test_redirect_active_link(self):
        """Активная ссылка перенаправляет на исходный URL."""
        response = self.client.get(self.redirect_url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response["Location"],
            self.link.original_url,
        )

    def test_redirect_increments_clicks_count(self):
        """Переход увеличивает счётчик кликов."""
        self.client.get(self.redirect_url)

        self.link.refresh_from_db()
        self.assertEqual(self.link.clicks_count, 1)

    def test_redirect_creates_click_record(self):
        """Переход создаёт запись аналитики."""
        initial_count = Click.objects.filter(link=self.link).count()

        self.client.get(self.redirect_url)

        self.assertEqual(
            Click.objects.filter(link=self.link).count(),
            initial_count + 1,
        )

    def test_redirect_unknown_code(self):
        """Несуществующий код возвращает 404."""
        response = self.client.get("/r/unknown123")

        self.assertEqual(response.status_code, 404)

    def test_redirect_inactive_link(self):
        """Неактивная ссылка возвращает 410."""
        self.link.is_active = False
        self.link.save(update_fields=["is_active"])

        response = self.client.get(self.redirect_url)

        self.assertEqual(response.status_code, 410)