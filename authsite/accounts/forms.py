import re

from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

User = get_user_model()

PHONE_RE = re.compile(r"^\+?\d{7,15}$")


def normalize_identifier(raw: str) -> str:
    """Return a canonical email (lower-cased) or phone number (digits and
    optional leading +). Raises ValidationError if it is neither."""
    value = (raw or "").strip()
    if "@" in value:
        validate_email(value)
        return value.lower()
    phone = re.sub(r"[\s\-().]", "", value)
    if PHONE_RE.match(phone):
        return phone
    raise ValidationError("Enter a valid email address or phone number.")


class LoginForm(forms.Form):
    identifier = forms.CharField(
        label="Email or Phone number",
        max_length=150,
        widget=forms.TextInput(attrs={"autocomplete": "username", "autofocus": True}),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        identifier = cleaned.get("identifier")
        password = cleaned.get("password")
        if identifier and password:
            try:
                username = normalize_identifier(identifier)
            except ValidationError:
                username = None
            self.user = (
                authenticate(self.request, username=username, password=password)
                if username
                else None
            )
            if self.user is None:
                # Same message for every failure so accounts can't be enumerated.
                raise ValidationError("Incorrect email/phone number or password.")
        return cleaned


class SignUpForm(forms.Form):
    name = forms.CharField(
        label="Name",
        max_length=150,
        widget=forms.TextInput(attrs={"autocomplete": "name", "autofocus": True}),
    )
    identifier = forms.CharField(
        label="Phone number or Email",
        max_length=150,
        widget=forms.TextInput(attrs={"autocomplete": "username"}),
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    def clean_identifier(self):
        username = normalize_identifier(self.cleaned_data["identifier"])
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("An account with this email or phone number already exists.")
        return username

    def clean(self):
        cleaned = super().clean()
        p1, p2 = cleaned.get("password1"), cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "The two passwords don't match.")
        elif p1:
            candidate = User(
                username=cleaned.get("identifier", ""),
                first_name=cleaned.get("name", ""),
            )
            try:
                validate_password(p1, candidate)
            except ValidationError as exc:
                self.add_error("password1", exc)
        return cleaned

    def save(self):
        username = self.cleaned_data["identifier"]
        email = username if "@" in username else ""
        return User.objects.create_user(
            username=username,
            email=email,
            password=self.cleaned_data["password1"],
            first_name=self.cleaned_data["name"].strip(),
        )
