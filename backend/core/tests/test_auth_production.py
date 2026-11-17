from django.test import override_settings
from rest_framework.test import APITestCase
from core.models import User, OneTimeCode

@override_settings(DEBUG=False)
class ProductionEmailAuthTests(APITestCase):
    def test_reset_never_discloses_a_token_from_client_debug_flag(self):
        User.objects.create_user(email="existing@example.com", password="Existing123!")
        response = self.client.post("/api/auth/forgot-password/", {"email": "existing@example.com", "debug": True}, format="json")
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("debug_reset_token", response.data)
        self.assertFalse(OneTimeCode.objects.exists())

    def test_registration_is_explicitly_unavailable_without_email_delivery(self):
        response = self.client.post("/api/auth/register/", {"email": "new@example.com", "password": "StrongPass123!", "debug": True}, format="json")
        self.assertEqual(response.status_code, 503)
        self.assertFalse(User.objects.filter(email="new@example.com").exists())
