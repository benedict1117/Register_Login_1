from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import LoginForm, SignUpForm


def _safe_next(request):
    target = request.POST.get("next") or request.GET.get("next") or ""
    if target and url_has_allowed_host_and_scheme(
        target, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return target
    return reverse("home")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = LoginForm(request, request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.user)
        return redirect(_safe_next(request))
    return render(
        request,
        "accounts/login.html",
        {"form": form, "next": request.GET.get("next", "")},
    )


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        return redirect("home")
    return render(request, "accounts/signup.html", {"form": form})


@require_POST
def logout_view(request):
    logout(request)
    return redirect("accounts:login")


@login_required
def home(request):
    return render(request, "accounts/home.html")
