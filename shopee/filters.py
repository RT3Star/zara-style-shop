from django.db.models import Q, Min, Max
from .models import Product, Category, Size, Color


class ProductFilter:
    def __init__(self, request, queryset=None):
        self.request = request
        self.queryset = queryset if queryset is not None else Product.objects.all()

    def filter_by_price(self):
        min_price = self.request.GET.get("min_price")
        max_price = self.request.GET.get("max_price")

        if min_price:
            try:
                min_price = float(min_price)
                self.queryset = self.queryset.filter(price__gte=min_price)
            except ValueError:
                pass

        if max_price:
            try:
                max_price = float(max_price)
                self.queryset = self.queryset.filter(price__lte=max_price)
            except ValueError:
                pass
        return self

    def filter_by_category(self):
        category = self.request.GET.get("category")
        if category:
            self.queryset = self.queryset.filter(category__slug=category)
        return self

    def filter_by_availability(self):
        in_stock = self.request.GET.get("in_stock")
        if in_stock == "true":
            self.queryset = self.queryset.filter(stock__gt=0)
        return self

    def filter_by_sizes(self):
        size = self.request.GET.get("size")
        if size:
            self.queryset = self.queryset.filter(sizes__name=size)
        return self

    def filter_by_colors(self):
        color = self.request.GET.get("color")
        if color:
            self.queryset = self.queryset.filter(colors__name=color)
        return self

    def filter_by_gender(self):
        gender = self.request.GET.get("gender")
        if gender:
            self.queryset = self.queryset.filter(gender=gender)
        return self

    def filter_by_discount(self):
        discounted = self.request.GET.get("discounted")
        if discounted == "true":
            self.queryset = self.queryset.filter(discount_price__isnull=False)
        return self

    def filter_by_search(self):
        search_query = self.request.GET.get("q")
        if search_query:
            self.queryset = self.queryset.filter(
                Q(name__icontains=search_query)
                | Q(description__icontains=search_query)
                | Q(category__name__icontains=search_query)
            )
        return self

    def sort_by(self):
        sort_option = self.request.GET.get("sort", "-created_at")

        allowed_sorts = {
            "price": "price",
            "-price": "-price",
            "name": "name",
            "-name": "-name",
            "created_at": "created_at",
            "-created_at": "-created_at",
            "popularity": "-views_count",
            "-popularity": "views_count",
            "rating": "-average_rating",
            "discount": "discount_price",
        }

        if sort_option in allowed_sorts:
            sort_field = allowed_sorts[sort_option]
            self.queryset = self.queryset.order_by(sort_field)
        else:
            self.queryset = self.queryset.order_by("-created_at")

        return self

    def filter_by_price_range(self):
        min_price = self.request.GET.get("min_price")
        max_price = self.request.GET.get("max_price")

        if min_price and max_price:
            try:
                self.queryset = self.queryset.filter(
                    price__gte=float(min_price), price__lte=float(max_price)
                )
            except ValueError:
                pass

        return self

    def get_queryset(self):
        self.queryset = self.queryset.select_related("category").prefetch_related(
            "images", "reviews", "sizes", "colors"
        )
        return self.queryset

    def get_price_range(self):
        price_range = self.queryset.aggregate(
            min_price=Min("price"), max_price=Max("price")
        )
        return {
            "min": price_range["min_price"] or 0,
            "max": price_range["max_price"] or 0,
        }

    def get_available_filters(self):
        available_filters = {
            "categories": list(
                Category.objects.filter(products__in=self.queryset)
                .distinct()
                .values("id", "name", "slug")
            ),
            "sizes": list(
                Size.objects.filter(products__in=self.queryset)
                .distinct()
                .values("id", "name")
            ),
            "colors": list(
                Color.objects.filter(products__in=self.queryset)
                .distinct()
                .values("id", "name", "code")
            ),
            "gender": self.queryset.values_list("gender", flat=True).distinct(),
        }
        return available_filters


def filter_products(request, queryset):
    filters = ProductFilter(request, queryset)
    filters.filter_by_price().filter_by_category().filter_by_availability().filter_by_sizes().filter_by_colors().filter_by_gender().filter_by_discount().sort_by()
    return filters.get_queryset()
