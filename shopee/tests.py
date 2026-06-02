from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache
from .models import Category, Product


class HomePageTest(TestCase):

    def test_home_page_status_code(self):
        response = self.client.get(reverse("shopee:home"))
        self.assertEqual(response.status_code, 200)


class ProductListTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create(
            name="Тестова категорія", slug="test-category", is_active=True
        )
        self.product = Product.objects.create(
            name="Тестовий товар",
            slug="test-product",
            description="Опис тестового товару",
            price=1000,
            category=self.category,
            stock=10,
            is_active=True,
        )

    def test_catalog_page_status(self):
        response = self.client.get(reverse("shopee:product_list"))
        self.assertEqual(response.status_code, 200)

    def test_filter_by_price(self):
        response = self.client.get(
            reverse("shopee:product_list"), {"min_price": 500, "max_price": 1500}
        )
        self.assertEqual(response.status_code, 200)


class UrlTest(TestCase):

    def test_home_url(self):
        response = self.client.get("/shop/")
        self.assertEqual(response.status_code, 200)

    def test_catalog_url(self):
        response = self.client.get("/shop/catalog/")
        self.assertEqual(response.status_code, 200)

    def test_search_url(self):
        response = self.client.get("/shop/search/")
        self.assertEqual(response.status_code, 200)

    def test_cart_url(self):
        response = self.client.get("/cart/")
        self.assertEqual(response.status_code, 200)

    def test_login_url(self):
        response = self.client.get("/users/login/")
        self.assertEqual(response.status_code, 200)

    def test_register_url(self):
        response = self.client.get("/users/register/")
        self.assertEqual(response.status_code, 200)


class CacheTest(TestCase):

    def setUp(self):
        cache.clear()

    def test_cache_works(self):
        cache_key = "test_key"
        cache.set(cache_key, "test_value", 60)
        self.assertEqual(cache.get(cache_key), "test_value")

    def test_cache_clear(self):
        cache_key = "test_key_2"
        cache.set(cache_key, "value", 60)
        cache.delete(cache_key)
        self.assertIsNone(cache.get(cache_key))


class ModelTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create(
            name="Категорія", slug="category-slug", is_active=True
        )
        self.product = Product.objects.create(
            name="Товар",
            slug="product-slug",
            description="Опис",
            price=500,
            category=self.category,
            stock=5,
            is_active=True,
        )

    def test_category_creation(self):
        self.assertEqual(self.category.name, "Категорія")
        self.assertEqual(self.category.slug, "category-slug")

    def test_product_creation(self):
        self.assertEqual(self.product.name, "Товар")
        self.assertEqual(self.product.price, 500)
        self.assertEqual(self.product.stock, 5)

    def test_product_str_method(self):
        self.assertEqual(str(self.product), "Товар")

    def test_category_str_method(self):
        self.assertEqual(str(self.category), "Категорія")
