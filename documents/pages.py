
from django import forms
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
)


class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        max_length=150,
        error_messages={
            "required": "Please enter a username.",
            "invalid": "Use letters, numbers, or @ . + - _ only.",
        },
        help_text=(
            "Use letters, numbers, or @ . + - _ only. "
            "Maximum 150 characters."
        ),
    )


def home(request):
    # Dashboard is only for logged-in users.
    if not request.user.is_authenticated:
        return redirect("login")

    return render(request, "documents/home.html")


def upload_page(request):
    if not request.user.is_authenticated:
        return redirect("login")

    return render(request, "documents/upload.html")


def login_page(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = AuthenticationForm(
        request,
        data=request.POST or None,
    )

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect("dashboard")

    return render(
        request,
        "documents/login.html",
        {"form": form},
    )


def signup_page(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = CustomUserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("dashboard")

    return render(
        request,
        "documents/signup.html",
        {"form": form},
    )


def logout_page(request):
    if request.method == "POST":
        logout(request)

    return redirect("login")
