from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken


User = get_user_model()


class RegistrationTests(APITestCase):
    register_url = "/api/auth/register/"

    def test_register_with_valid_data(self):
        """Регистрация с корректными данными."""
        response = self.client.post(
            self.register_url,
            {
                "username": "testuser",
                "email": "testuser@example.com",
                "password": "S3cure!Random-Password-927",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            User.objects.filter(username="testuser").exists()
        )

        user = User.objects.get(username="testuser")
        self.assertTrue(
            user.check_password("S3cure!Random-Password-927")
        )

    def test_register_with_duplicate_username(self):
        """Повторное имя пользователя отклоняется."""
        User.objects.create_user(
            username="existinguser",
            email="existing@example.com",
            password="S3cure!Random-Password-927",
        )

        response = self.client.post(
            self.register_url,
            {
                "username": "existinguser",
                "email": "another@example.com",
                "password": "An0ther!Secure-Password-927",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            User.objects.filter(username__iexact="existinguser").count(),
            1,
        )

    def test_register_with_weak_password(self):
        """Слабый пароль отклоняется."""
        response = self.client.post(
            self.register_url,
            {
                "username": "weakpassuser",
                "email": "weakpass@example.com",
                "password": "123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(
            User.objects.filter(username="weakpassuser").exists()
        )


class AuthenticationTests(APITestCase):
    token_url = "/api/auth/token/"
    me_url = "/api/auth/me/"

    def setUp(self):
        self.username = "authuser"
        self.password = "S3cure!Random-Password-927"

        self.user = User.objects.create_user(
            username=self.username,
            email="authuser@example.com",
            password=self.password,
        )

    def test_obtain_access_token(self):
        """Получение access-токена по логину и паролю."""
        response = self.client.post(
            self.token_url,
            {
                "username": self.username,
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_protected_endpoint_without_token(self):
        """Защищённый endpoint без токена возвращает 401."""
        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_protected_endpoint_with_invalid_token(self):
        """Некорректный JWT отклоняется."""
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer invalid.token.value"
        )

        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_protected_endpoint_with_expired_token(self):
        """Истёкший JWT отклоняется."""
        token = AccessToken.for_user(self.user)
        token["exp"] = int(
            (timezone.now() - timedelta(minutes=1)).timestamp()
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {str(token)}"
        )

        response = self.client.get(self.me_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)