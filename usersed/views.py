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
import time



def check_rate_limit(request, key, limit=5, period=60):
    print(f"CHECKING RATE LIMIT: {key}")
    cache_key = f'rate_limit_{key}'
    attempts = cache.get(cache_key, 0)
    print(f"Attempts: {attempts}")

    if attempts >= limit:
        return False

    cache.set(cache_key, attempts + 1, period)
    return True


def register_view(request):

    ip = request.META.get('REMOTE_ADDR')
    if not check_rate_limit(request, f'register_{ip}', limit=5, period=60):
        messages.error(request, '❌ Забагато спроб реєстрації. Зачекайте 1 хвилину.')
        return redirect('usersed:register')



def login_view(request):

    ip = request.META.get('REMOTE_ADDR')
    if not check_rate_limit(request, f'login_{ip}', limit=5, period=60):
        messages.error(request, '❌ Забагато спроб входу. Зачекайте 1 хвилину.')
        return redirect('usersed:login')



def logout_view(request):
    logout(request)
    messages.info(request, "Ви вийшли з акаунту.")
    return redirect("home")


@login_required
def profile_view(request):
    return render(request, "usersed/profile.html", {"user": request.user})


@login_required
def profile_edit_view(request):
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
    if request.method == "POST":
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "Ваш аккаунт видалено.")
        return redirect("home")

    return render(request, "usersed/delete_profile.html")


def rate_limit_exceeded(request, exception):
    messages.error(request, '❌ Забагато спроб. Зачекайте 1 хвилину.')
    return redirect(request.META.get('HTTP_REFERER', 'usersed:login'))


def handler403(request, exception=None):
    return render(request, "403.html", status=403)


def handler404(request, exception=None):
    return render(request, "404.html", status=404)


def handler500(request):
    return render(request, "500.html", status=500)