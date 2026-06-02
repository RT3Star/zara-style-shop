from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


def send_order_confirmation_email(order):
    """Відправка email підтвердження замовлення"""

    # Формуємо список товарів
    items_html = ""
    items_text = ""
    for item in order.items.all():
        items_html += f"""
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #eee;">{item.product_name}</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee;">{item.quantity}</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee;">{item.product_price} ₴</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee;">{item.total_price()} ₴</td>
            </tr>
        """
        items_text += (
            f"{item.product_name} x {item.quantity} = {item.total_price()} ₴\n"
        )

    # HTML шаблон для email
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Підтвердження замовлення</title>
    </head>
    <body style="font-family: 'Montserrat', Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="text-align: center; padding: 20px; background: #000; color: #fff;">
            <h1 style="margin: 0;">ZARA STYLE</h1>
        </div>

        <div style="padding: 20px;">
            <h2>Дякуємо за замовлення, {order.first_name}!</h2>
            <p>Ваше замовлення <strong>#{order.id}</strong> прийнято в обробку.</p>

            <div style="background: #f8f8f8; padding: 15px; margin: 20px 0;">
                <h3 style="margin-top: 0;">Деталі замовлення:</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="background: #000; color: #fff;">
                            <th style="padding: 10px;">Товар</th>
                            <th style="padding: 10px;">Кількість</th>
                            <th style="padding: 10px;">Ціна</th>
                            <th style="padding: 10px;">Сума</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items_html}
                    </tbody>
                </table>

                <div style="margin-top: 20px; text-align: right;">
                    <p><strong>Доставка:</strong> {order.delivery_price} ₴</p>
                    <p style="font-size: 1.2rem;"><strong>ВСЬОГО:</strong> {order.total_price} ₴</p>
                </div>
            </div>

            <div style="margin: 20px 0;">
                <h3>Інформація про доставку:</h3>
                <p>{order.first_name} {order.last_name}</p>
                <p>{order.address}</p>
                <p>{order.city}</p>
                <p>📞 {order.phone}</p>
            </div>

            <div style="margin: 20px 0;">
                <h3>Статус замовлення:</h3>
                <p>🟡 {order.get_status_display()}</p>
                <p>Ви можете відстежувати статус замовлення в особистому кабінеті.</p>
            </div>

            <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #999;">
                <p>© 2024 ZARA STYLE. Всі права захищені.</p>
            </div>
        </div>
    </body>
    </html>
    """

    # Текстова версія для email
    text_content = f"""
    Дякуємо за замовлення, {order.first_name}!

    Ваше замовлення #{order.id} прийнято в обробку.

    Товари:
    {items_text}

    Доставка: {order.delivery_price} ₴
    ВСЬОГО: {order.total_price} ₴

    Статус: {order.get_status_display()}
    """

    send_mail(
        subject=f"Підтвердження замовлення #{order.id} - ZARA STYLE",
        message=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.email],
        fail_silently=False,
        html_message=html_content,
    )


def send_order_status_update_email(order, old_status, new_status):
    """Відправка email при зміні статусу замовлення"""

    status_messages = {
        "processing": "Ваше замовлення прийнято в обробку",
        "shipped": "Ваше замовлення відправлено!",
        "delivered": "Ваше замовлення доставлено",
        "cancelled": "Ваше замовлення скасовано",
    }

    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: #000; color: #fff; text-align: center; padding: 20px;">
            <h1>ZARA STYLE</h1>
        </div>
        <div style="padding: 20px;">
            <h2>Статус замовлення #{order.id} змінено</h2>
            <p>Статус: <strong>{order.get_status_display()}</strong></p>
            <p>{status_messages.get(new_status, 'Статус замовлення оновлено')}</p>
            <a href="http://127.0.0.1:8000/orders/{order.id}/" style="background: #000; color: #fff; padding: 10px 20px; text-decoration: none;">Деталі замовлення</a>
        </div>
    </body>
    </html>
    """

    send_mail(
        subject=f"Статус замовлення #{order.id} змінено",
        message=status_messages.get(new_status, "Статус замовлення оновлено"),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.email],
        fail_silently=False,
        html_message=html_content,
    )
