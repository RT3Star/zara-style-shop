from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("create/", views.order_create_view, name="order_create"),
    path("", views.order_list_view, name="order_list"),
    path("<int:order_id>/", views.order_detail_view, name="order_detail"),
    path("<int:order_id>/cancel/", views.order_cancel_view, name="order_cancel"),
    path("<int:order_id>/repeat/", views.order_repeat_view, name="order_repeat"),
    path("<int:order_id>/tracking/", views.order_tracking_view, name="order_tracking"),
]
