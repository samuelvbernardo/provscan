from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.validators import StrongPasswordValidator

User = get_user_model()


class UserManagerTests(TestCase):
    def test_create_user_normalizes_email(self):
        # normalize_email lowercases only the domain, not the local part
        user = User.objects.create_user(email="TEST@EXAMPLE.COM", password="pass")
        self.assertEqual(user.email, "TEST@example.com")

    def test_create_user_requires_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="pass")

    def test_create_superuser_sets_flags(self):
        user = User.objects.create_superuser(email="admin@example.com", password="pass")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_create_superuser_requires_is_staff(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="admin@example.com", password="pass", is_staff=False
            )


class StrongPasswordValidatorTests(TestCase):
    def setUp(self):
        self.validator = StrongPasswordValidator()

    def _assert_invalid(self, password, code):
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError) as ctx:
            self.validator.validate(password)
        codes = [e.code for e in ctx.exception.error_list]
        self.assertIn(code, codes)

    def test_valid_password(self):
        self.assertIsNone(self.validator.validate("Secure@123"))

    def test_too_short(self):
        self._assert_invalid("Ab@1", "password_too_short")

    def test_no_uppercase(self):
        self._assert_invalid("secure@123", "password_no_upper")

    def test_no_lowercase(self):
        self._assert_invalid("SECURE@123", "password_no_lower")

    def test_no_digit(self):
        self._assert_invalid("Secure@abc", "password_no_number")

    def test_no_special(self):
        self._assert_invalid("Secure1234", "password_no_special")


class TokenEndpointTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@example.com", password="Test@1234"
        )

    def test_login_returns_tokens(self):
        res = self.client.post(
            "/api/token/",
            {"email": "user@example.com", "password": "Test@1234"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)

    def test_login_wrong_password_returns_401(self):
        res = self.client.post(
            "/api/token/",
            {"email": "user@example.com", "password": "errada"},
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_missing_fields_returns_400(self):
        res = self.client.post("/api/token/", {}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class UserCreateAPITests(APITestCase):
    URL = "/api/v1/users/"

    @patch("accounts.api.v1.serializers.validate_email_domain_exists")
    def test_create_user_valid(self, mock_dns):
        mock_dns.return_value = None
        res = self.client.post(
            self.URL,
            {
                "email": "novo@example.com",
                "password": "Secure@123",
                "password_confirm": "Secure@123",
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="novo@example.com").exists())

    @patch("accounts.api.v1.serializers.validate_email_domain_exists")
    def test_create_user_password_mismatch(self, mock_dns):
        mock_dns.return_value = None
        res = self.client.post(
            self.URL,
            {
                "email": "novo2@example.com",
                "password": "Secure@123",
                "password_confirm": "Diferente@123",
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password_confirm", res.data)

    @patch("accounts.api.v1.serializers.validate_email_domain_exists")
    def test_create_user_duplicate_email(self, mock_dns):
        mock_dns.return_value = None
        User.objects.create_user(email="existente@example.com", password="Secure@123")
        res = self.client.post(
            self.URL,
            {
                "email": "existente@example.com",
                "password": "Secure@123",
                "password_confirm": "Secure@123",
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("accounts.api.v1.serializers.validate_email_domain_exists")
    def test_create_user_weak_password(self, mock_dns):
        mock_dns.return_value = None
        res = self.client.post(
            self.URL,
            {
                "email": "fraco@example.com",
                "password": "12345678",
                "password_confirm": "12345678",
            },
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_users_requires_auth(self):
        res = self.client.get(self.URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
