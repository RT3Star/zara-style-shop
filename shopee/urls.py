from django.urls import path
from . import views

app_name = "shopee"

urlpatterns = [
    path("", views.home_view, name="home"),
    path("catalog/", views.product_list_view, name="product_list"),
    path(
        "catalog/category/<slug:slug>/",
        views.category_products_view,
        name="category_products",
    ),
    path("product/<slug:slug>/", views.product_detail_view, name="product_detail"),
    path("search/", views.search_view, name="search"),
    path("review/<int:product_id>/", views.add_review_view, name="add_review"),
    path("api/filters/", views.get_product_filters, name="api_filters"),
    path("admin/dashboard/", views.admin_dashboard, name="admin_dashboard"),
]
