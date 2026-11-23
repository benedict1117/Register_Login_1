from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class AuthFlowTests(TestCase):
    def signup(self, identifier="09369945251", **overrides):
        data = {
            "name": "Ana Cruz",
            "identifier": identifier,
            "password1": "S7rong-pass-phrase",
            "password2": "S7rong-pass-phrase",
        }
        data.update(overrides)
        return self.client.post(reverse("accounts:signup"), data)

    def test_pages_render(self):
        self.assertContains(self.client.get(reverse("accounts:login")), "Log In")
        self.assertContains(self.client.get(reverse("accounts:signup")), "Create Account")

    def test_signup_with_phone_logs_in(self):
        resp = self.signup()
        self.assertRedirects(resp, reverse("home"))
        user = User.objects.get(username="09369945251")
        self.assertEqual(user.first_name, "Ana Cruz")

    def test_signup_with_email_is_lowercased(self):
        self.signup("Ana@Example.COM")
        self.assertTrue(User.objects.filter(username="ana@example.com", email="ana@example.com").exists())

    def test_signup_rejects_duplicate_and_mismatch(self):
        self.signup()
        self.client.logout()
        self.assertContains(self.signup(), "already exists")
        self.assertContains(self.signup("09170000000", password2="different"), "don&#x27;t match")

    def test_signup_rejects_bad_identifier(self):
        self.assertContains(self.signup("not-a-contact"), "valid email address or phone")

    def test_login_logout(self):
        self.signup()
        self.client.post(reverse("accounts:logout"))
        resp = self.client.post(
            reverse("accounts:login"),
            {"identifier": "0936 994 5251", "password": "S7rong-pass-phrase"},
        )
        self.assertRedirects(resp, reverse("home"))

    def test_login_wrong_password(self):
        self.signup()
        self.client.post(reverse("accounts:logout"))
        resp = self.client.post(
            reverse("accounts:login"),
            {"identifier": "09369945251", "password": "nope"},
        )
        self.assertContains(resp, "Incorrect email/phone number or password.")

    def test_home_requires_login(self):
        resp = self.client.get(reverse("home"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse("accounts:login"), resp["Location"])
