from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg, Min, Max, F
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from .models import Product, Category, Size, Color, Review
from .filters import ProductFilter
from .admin_dashboard import DashboardStats
from django.views.decorators.cache import cache_page
from django.core.cache import cache


@cache_page(60 * 5)
def home_view(request):

    new_products = Product.objects.filter(is_active=True).order_by("-created_at")[:8]

    popular_products = Product.objects.filter(is_active=True).order_by("-views_count")[
        :8
    ]

    discounted_products = Product.objects.filter(
        is_active=True, discount_price__isnull=False
    )[:8]

    bestsellers = Product.objects.filter(is_active=True, is_bestseller=True)[:8]

    categories = Category.objects.annotate(
        product_count=Count("products", filter=Q(products__is_active=True))
    ).filter(product_count__gt=0)[:6]

    context = {
        "new_products": new_products,
        "popular_products": popular_products,
        "discounted_products": discounted_products,
        "bestsellers": bestsellers,
        "categories": categories,
    }
    return render(request, "shopee/home.html", context)


def search_view(request):
    query = request.GET.get("q", "")
    products = Product.objects.filter(is_active=True)

    if query and query not in request.session.get("search_history", []):
        search_history = request.session.get("search_history", [])
        search_history.insert(0, query)
        request.session["search_history"] = search_history[:5]

    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(category__name__icontains=query)
        ).select_related("category")

    popular_searches = ["футболка", "джинси", "кросівки", "світшот", "пальто", "сукня"]

    context = {
        "products": products,
        "query": query,
        "count": products.count(),
        "search_history": request.session.get("search_history", []),
        "popular_searches": popular_searches,
    }
    return render(request, "shopee/search.html", context)


def product_detail_view(request, slug):
    cache_key = f"product_detail_{slug}"

    cached_response = cache.get(cache_key)
    if cached_response:
        return cached_response

    product = get_object_or_404(Product, slug=slug, is_active=True)

    product.views_count = F("views_count") + 1
    product.save()
    product.refresh_from_db()

    viewed_products = request.session.get("viewed_products", [])
    if product.id not in viewed_products:
        viewed_products.insert(0, product.id)
        request.session["viewed_products"] = viewed_products[:10]

    recommendations = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(id=product.id)[:8]

    if recommendations.count() < 8:
        more_recommendations = (
            Product.objects.filter(is_active=True)
            .exclude(id=product.id)
            .exclude(id__in=recommendations)[: 8 - recommendations.count()]
        )
        recommendations = list(recommendations) + list(more_recommendations)

    reviews = product.reviews.filter(is_approved=True)[:10]
    average_rating = product.average_rating

    user_review = None
    if request.user.is_authenticated:
        user_review = product.reviews.filter(user=request.user).first()

    context = {
        "product": product,
        "recommendations": recommendations,
        "viewed_products": request.session.get("viewed_products", []),
        "reviews": reviews,
        "average_rating": average_rating,
        "user_review": user_review,
        "sizes": product.sizes.all(),
        "colors": product.colors.all(),
    }
    response = render(request, "shopee/product_detail.html", context)
    cache.set(cache_key, response, 300)  # 5 хвилин
    return response


def product_list_view(request):

    cache_key = f"product_list_{request.GET.urlencode()}"

    cached_response = cache.get(cache_key)
    if cached_response:
        return cached_response

    products = (
        Product.objects.select_related("category")
        .prefetch_related("images", "sizes", "colors")
        .filter(is_active=True)
    )

    product_filter = ProductFilter(request, products)
    product_filter.filter_by_price().filter_by_category().filter_by_availability()
    product_filter.filter_by_sizes().filter_by_colors().filter_by_gender()
    products = product_filter.sort_by().get_queryset()

    paginator = Paginator(products, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.filter(
        products__isnull=False, products__is_active=True
    ).distinct()
    sizes = Size.objects.filter(products__isnull=False).distinct()
    colors = Color.objects.filter(products__isnull=False).distinct()

    price_range = Product.objects.filter(is_active=True).aggregate(
        min_price=Min("price"), max_price=Max("price")
    )

    context = {
        "products": page_obj,
        "categories": categories,
        "sizes": sizes,
        "colors": colors,
        "price_range": price_range,
        "current_filters": {
            "min_price": request.GET.get("min_price"),
            "max_price": request.GET.get("max_price"),
            "category": request.GET.get("category"),
            "sort": request.GET.get("sort", "-created_at"),
            "in_stock": request.GET.get("in_stock"),
            "size": request.GET.get("size"),
            "color": request.GET.get("color"),
            "gender": request.GET.get("gender"),
        },
    }

    response = render(request, "shopee/product_list.html", context)
    cache.set(cache_key, response, 300)  # 5 хвилин

    return response


@require_POST
def add_review_view(request, product_id):
    if not request.user.is_authenticated:
        messages.error(request, "Увійдіть в акаунт, щоб залишити відгук")
        return redirect("usersed:login")

    product = get_object_or_404(Product, id=product_id, is_active=True)

    if Review.objects.filter(product=product, user=request.user).exists():
        messages.error(request, "Ви вже залишали відгук на цей товар")
        return redirect("shopee:product_detail", slug=product.slug)

    rating = request.POST.get("rating")
    comment = request.POST.get("comment")

    if rating and comment:
        Review.objects.create(
            product=product, user=request.user, rating=int(rating), comment=comment
        )
        messages.success(request, "Дякуємо за ваш відгук!")
    else:
        messages.error(request, "Будь ласка, заповніть всі поля")

    return redirect("shopee:product_detail", slug=product.slug)


def category_products_view(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(category=category, is_active=True)

    context = {
        "category": category,
        "products": products,
    }
    return render(request, "shopee/category_products.html", context)


def get_product_filters(request):
    filters = {
        "categories": list(
            Category.objects.filter(products__isnull=False)
            .values("id", "name", "slug")
            .distinct()
        ),
        "sizes": list(Size.objects.values("id", "name")),
        "colors": list(Color.objects.values("id", "name", "code")),
        "price_range": Product.objects.filter(is_active=True).aggregate(
            min_price=Min("price"), max_price=Max("price")
        ),
        "genders": [
            {"value": "M", "label": "Чоловічий"},
            {"value": "F", "label": "Жіночий"},
            {"value": "U", "label": "Унісекс"},
            {"value": "K", "label": "Дитячий"},
        ],
    }
    return JsonResponse(filters)


# ========== АДМІН ДАШБОРД ==========


@staff_member_required
def admin_dashboard(request):
    stats = DashboardStats.get_stats()

    context = {
        "stats": stats,
        "chart_labels": ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"],
    }
    return render(request, "shopee/admin_dashboard.html", context)
