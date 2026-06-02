from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    PasswordChangeForm,
)
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.db import IntegrityError
from django_ratelimit.decorators import ratelimit

from .forms import UserRegistrationForm, UserProfileForm, UserUpdateForm
from .models import UserProfile
from django_ratelimit.decorators import ratelimit
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django_ratelimit.exceptions import Ratelimited
from django.http import HttpResponseForbidden
from django.shortcuts import render


@ratelimit(key="ip", rate="5/m", method="POST", block=True)
def register_view(request):
    """Реєстрація нового користувача"""

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                messages.success(
                    request, f"Вітаємо, {user.username}! Ви успішно зареєструвалися."
                )
                return redirect("home")
            except IntegrityError:
                messages.error(
                    request, "Помилка при створенні профілю. Спробуйте ще раз."
                )
                form = UserRegistrationForm()
        else:
            messages.error(request, "Будь ласка, виправте помилки у формі.")
    else:
        form = UserRegistrationForm()

    return render(request, "usersed/register.html", {"form": form})


@ratelimit(key="ip", rate="10/m", method="POST", block=True)
def login_view(request):
    """Вхід користувача"""

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Ласкаво просимо назад, {user.username}!")
            next_url = request.GET.get("next", "home")
            return redirect(next_url)
        else:
            messages.error(request, "Неправильне ім'я користувача або пароль.")
    else:
        form = AuthenticationForm()

    return render(request, "usersed/login.html", {"form": form})


def logout_view(request):
    """Вихід користувача"""
    logout(request)
    messages.info(request, "Ви вийшли з акаунту.")
    return redirect("home")


@login_required
def profile_view(request):
    """Перегляд профілю користувача"""
    return render(request, "usersed/profile.html", {"user": request.user})


@login_required
def profile_edit_view(request):
    """Редагування профілю користувача"""
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)

    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Ваш профіль успішно оновлено!")
            return redirect("usersed:profile")
        else:
            messages.error(request, "Будь ласка, виправте помилки у формі.")
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)

    context = {
        "user_form": user_form,
        "profile_form": profile_form,
    }
    return render(request, "usersed/profile_edit.html", context)


@login_required
def change_password_view(request):
    """Зміна пароля користувача"""
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Ваш пароль успішно змінено!")
            return redirect("usersed:profile")
        else:
            messages.error(request, "Будь ласка, виправте помилки.")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "usersed/change_password.html", {"form": form})


@login_required
def delete_profile_view(request):
    """Видалення профілю користувача"""
    if request.method == "POST":
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "Ваш аккаунт видалено.")
        return redirect("home")

    return render(request, "usersed/delete_profile.html")


def rate_limit_exceeded(request, exception):
    """Обробник перевищення ліміту запитів"""
    messages.error(
        request,
        "❌ Забагато невдалих спроб. Зачекайте 1 хвилину перед наступною спробою.",
    )
    # Повертаємо на ту ж сторінку
    return redirect(request.META.get("HTTP_REFERER", "usersed:login"))


def handler403(request, exception=None):
    """Обробник помилки 403 Forbidden"""
    return render(request, "403.html", status=403)


def handler404(request, exception=None):
    """Обробник помилки 404 Not Found"""
    return render(request, "404.html", status=404)


def handler500(request):
    """Обробник помилки 500 Internal Server Error"""
    return render(request, "500.html", status=500)
