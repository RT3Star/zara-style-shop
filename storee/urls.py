"""
URL configuration for storee project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from usersed import views as usersed_views
from django.views.static import serve
from django.urls import re_path

handler403 = usersed_views.handler403
handler404 = usersed_views.handler404
handler500 = usersed_views.handler500

urlpatterns = [
    path("admin/", admin.site.urls),
    # Головна сторінка - перенаправляє на shop/
    path("", RedirectView.as_view(url="/shop/", permanent=False), name="home"),
    path("shop/", include("shopee.urls")),
    path("cart/", include("cart.urls")),
    path("orders/", include("orders.urls")),
    path("users/", include("usersed.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if not settings.DEBUG:
    urlpatterns += [
        re_path(
            r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}
        ),
        re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    ]
