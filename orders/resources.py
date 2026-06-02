# orders/resources.py
from import_export import resources
from import_export.fields import Field
from .models import Order, OrderItem


class OrderItemResource(resources.ModelResource):
    """Ресурс для експорту товарів замовлення"""

    product_name = Field(attribute="product_name", column_name="Назва товару")
    quantity = Field(attribute="quantity", column_name="Кількість")
    price = Field(attribute="product_price", column_name="Ціна")
    total = Field(attribute="total_price", column_name="Сума")

    class Meta:
        model = OrderItem
        fields = ("product_name", "quantity", "price", "total")
        export_order = ("product_name", "quantity", "price", "total")


class OrderResource(resources.ModelResource):
    """Ресурс для експорту замовлень"""

    order_id = Field(attribute="id", column_name="№ Замовлення")
    customer_name = Field(attribute="get_full_name", column_name="Клієнт")
    customer_email = Field(attribute="email", column_name="Email")
    customer_phone = Field(attribute="phone", column_name="Телефон")
    total = Field(attribute="total_price", column_name="Сума, грн")
    status = Field(attribute="get_status_display", column_name="Статус")
    payment = Field(attribute="get_payment_method_display", column_name="Оплата")
    delivery = Field(attribute="get_delivery_method_display", column_name="Доставка")
    created = Field(attribute="created_at", column_name="Дата створення")

    class Meta:
        model = Order
        fields = (
            "order_id",
            "customer_name",
            "customer_email",
            "customer_phone",
            "total",
            "status",
            "payment",
            "delivery",
            "created",
        )
        export_order = (
            "order_id",
            "customer_name",
            "customer_email",
            "customer_phone",
            "total",
            "status",
            "payment",
            "delivery",
            "created",
        )
