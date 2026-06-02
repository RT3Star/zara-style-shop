from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import Product, Category, Review
from orders.models import Order
from usersed.models import CustomUser


class DashboardStats:
    """Клас для збору статистики для дашборду"""

    @staticmethod
    def get_stats():
        """Отримання всієї статистики"""
        today = timezone.now()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        # Загальна статистика
        total_products = Product.objects.filter(is_active=True).count()
        total_categories = Category.objects.filter(is_active=True).count()
        total_users = CustomUser.objects.count()
        total_orders = Order.objects.count()

        # Статистика замовлень
        orders_today = Order.objects.filter(created_at__date=today.date()).count()
        orders_week = Order.objects.filter(created_at__gte=week_ago).count()
        orders_month = Order.objects.filter(created_at__gte=month_ago).count()

        # Сума замовлень
        revenue_today = (
            Order.objects.filter(
                created_at__date=today.date(), status="delivered"
            ).aggregate(Sum("total_price"))["total_price__sum"]
            or 0
        )
        revenue_week = (
            Order.objects.filter(
                created_at__gte=week_ago, status="delivered"
            ).aggregate(Sum("total_price"))["total_price__sum"]
            or 0
        )
        revenue_month = (
            Order.objects.filter(
                created_at__gte=month_ago, status="delivered"
            ).aggregate(Sum("total_price"))["total_price__sum"]
            or 0
        )

        # Замовлення за статусами
        orders_by_status = {
            "pending": Order.objects.filter(status="pending").count(),
            "processing": Order.objects.filter(status="processing").count(),
            "shipped": Order.objects.filter(status="shipped").count(),
            "delivered": Order.objects.filter(status="delivered").count(),
            "cancelled": Order.objects.filter(status="cancelled").count(),
        }

        # Товари з низьким залишком
        low_stock_products = Product.objects.filter(stock__lt=10, is_active=True)[:10]

        # Популярні товари
        popular_products = Product.objects.filter(is_active=True).order_by(
            "-views_count"
        )[:10]

        # Останні замовлення
        recent_orders = Order.objects.all().order_by("-created_at")[:10]

        # Топ категорій
        top_categories = Category.objects.annotate(
            product_count=Count("products", filter=Q(products__is_active=True))
        ).order_by("-product_count")[:5]

        # Відгуки без відповіді
        unreplied_reviews = Review.objects.filter(
            admin_reply__isnull=True, is_approved=True
        ).count()

        return {
            "total_products": total_products,
            "total_categories": total_categories,
            "total_users": total_users,
            "total_orders": total_orders,
            "orders_today": orders_today,
            "orders_week": orders_week,
            "orders_month": orders_month,
            "revenue_today": revenue_today,
            "revenue_week": revenue_week,
            "revenue_month": revenue_month,
            "orders_by_status": orders_by_status,
            "low_stock_products": low_stock_products,
            "popular_products": popular_products,
            "recent_orders": recent_orders,
            "top_categories": top_categories,
            "unreplied_reviews": unreplied_reviews,
        }
