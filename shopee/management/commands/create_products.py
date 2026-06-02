from django.core.management.base import BaseCommand
from shopee.models import Category, Product, Size, Color
from django.core.files.base import ContentFile
import urllib.request
from PIL import Image
from io import BytesIO


class Command(BaseCommand):
    help = "Створює тестові товари для магазину"

    def download_image(self, url, product_name):
        """Завантажує зображення з URL"""
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as response:
                return ContentFile(response.read(), name=f"{product_name}.jpg")
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(
                    f"  ⚠️ Не вдалося завантажити зображення для {product_name}: {e}"
                )
            )
            return None

    def handle(self, *args, **kwargs):
        # Створення категорій
        categories_data = [
            {"name": "Сукні", "slug": "sukni"},
            {"name": "Сорочки", "slug": "sorochki"},
            {"name": "Джинси", "slug": "dzhynsy"},
            {"name": "Пальта", "slug": "palta"},
            {"name": "Світшоти", "slug": "svitshoty"},
            {"name": "Взуття", "slug": "vzuttya"},
            {"name": "Аксесуари", "slug": "aksesuary"},
            {"name": "Футболки", "slug": "futbolky"},
            {"name": "Шорти", "slug": "shorty"},
        ]

        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data["slug"],
                defaults={"name": cat_data["name"], "is_active": True},
            )
            self.stdout.write(
                f'{"Створено" if created else "Існує"} категорію: {category.name}'
            )

        # Створення розмірів
        sizes_data = [
            "XS",
            "S",
            "M",
            "L",
            "XL",
            "XXL",
            "36",
            "37",
            "38",
            "39",
            "40",
            "41",
            "42",
            "43",
            "44",
        ]
        for size_name in sizes_data:
            Size.objects.get_or_create(name=size_name)
        self.stdout.write(f"Створено {Size.objects.count()} розмірів")

        # Створення кольорів
        colors_data = [
            {"name": "Чорний", "code": "#000000"},
            {"name": "Білий", "code": "#FFFFFF"},
            {"name": "Сірий", "code": "#808080"},
            {"name": "Синій", "code": "#0000FF"},
            {"name": "Червоний", "code": "#FF0000"},
            {"name": "Бежевий", "code": "#F5F5DC"},
            {"name": "Зелений", "code": "#008000"},
            {"name": "Жовтий", "code": "#FFFF00"},
            {"name": "Рожевий", "code": "#FFC0CB"},
            {"name": "Фіолетовий", "code": "#800080"},
            {"name": "Коричневий", "code": "#8B4513"},
            {"name": "Золотий", "code": "#FFD700"},
            {"name": "Оливковий", "code": "#808000"},
        ]

        for color_data in colors_data:
            Color.objects.get_or_create(
                name=color_data["name"], defaults={"code": color_data["code"]}
            )
        self.stdout.write(f"Створено {Color.objects.count()} кольорів")

        # Товари з реальними зображеннями (БІЛЬШЕ ТОВАРІВ)
        # Товари з реальними зображеннями
        products_data = [
            # ===== СУКНІ =====
            {
                "name": "Елегантна вечірня сукня",
                "slug": "vechirnya-suknya",
                "description": "Розкішна вечірня сукня з шовку. Ідеальний вибір для особливих подій.",
                "price": 4599,
                "discount_price": 3599,
                "category_slug": "sukni",
                "stock": 12,
                "gender": "F",
                "sizes": ["XS", "S", "M", "L"],
                "colors": ["Чорний", "Червоний", "Синій"],
                "image_url": "https://images.unsplash.com/photo-1566174053879-31528523f8ae?w=600",
            },
            {
                "name": "Лляна сукня міді",
                "slug": "llyana-suknya",
                "description": "Легка льняна сукня для спекотного літа. Натуральний матеріал.",
                "price": 2890,
                "discount_price": None,
                "category_slug": "sukni",
                "stock": 25,
                "gender": "F",
                "sizes": ["S", "M", "L", "XL"],
                "colors": ["Бежевий", "Білий", "Зелений"],
                "image_url": "https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=600",
            },
            {
                "name": "Сукня-футляр",
                "slug": "suknya-futlyar",
                "description": "Стильна сукня-футляр для офісу. Класичний крій.",
                "price": 3490,
                "discount_price": 2990,
                "category_slug": "sukni",
                "stock": 18,
                "gender": "F",
                "sizes": ["XS", "S", "M", "L", "XL"],
                "colors": ["Чорний", "Синій", "Сірий"],
                "image_url": "https://images.unsplash.com/photo-1581044777550-4cfa60707c03?w=600",
            },
            # ===== ДЖИНСИ =====
            {
                "name": "Класичні джинси straight",
                "slug": "dzhynsy-straight",
                "description": "Класичні джинси прямого крою з високоякісного деніму.",
                "price": 2190,
                "discount_price": 1890,
                "category_slug": "dzhynsy",
                "stock": 45,
                "gender": "M",
                "sizes": ["S", "M", "L", "XL", "XXL"],
                "colors": ["Синій", "Чорний", "Сірий"],
                "image_url": "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=600",
            },
            {
                "name": "Скінні джинси",
                "slug": "skinni-dzhynsy",
                "description": "Еластичні скінні джинси, які підкреслюють фігуру.",
                "price": 1990,
                "discount_price": None,
                "category_slug": "dzhynsy",
                "stock": 30,
                "gender": "F",
                "sizes": ["XS", "S", "M", "L"],
                "colors": ["Синій", "Чорний", "Сірий"],
                "image_url": "https://images.unsplash.com/photo-1582552938357-32b906df40cb?w=600",
            },
            {
                "name": "Клеш джинси",
                "slug": "klesh-dzhynsy",
                "description": "Модні джинси-клеш. Повернення стилю 70-х.",
                "price": 2390,
                "discount_price": 1990,
                "category_slug": "dzhynsy",
                "stock": 22,
                "gender": "F",
                "sizes": ["S", "M", "L"],
                "colors": ["Синій", "Чорний"],
                "image_url": "https://images.unsplash.com/photo-1582418702059-97ebafb35d09?w=600",
            },
            # ===== ФУТБОЛКИ =====
            {
                "name": "Базові білі футболки",
                "slug": "bazovi-bili-futbolky",
                "description": "Набір з 3 базових білих футболок. 100% бавовна.",
                "price": 990,
                "discount_price": 790,
                "category_slug": "futbolky",
                "stock": 100,
                "gender": "M",
                "sizes": ["S", "M", "L", "XL", "XXL"],
                "colors": ["Білий"],
                "image_url": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=600",
            },
            {
                "name": "Футболка з принтом",
                "slug": "futbolka-prynt",
                "description": "Стильна футболка з модним принтом. Вільний крій.",
                "price": 890,
                "discount_price": None,
                "category_slug": "futbolky",
                "stock": 35,
                "gender": "M",
                "sizes": ["S", "M", "L", "XL"],
                "colors": ["Чорний", "Білий", "Сірий"],
                "image_url": "https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?w=600",
            },
            # ===== СВІТШОТИ =====
            {
                "name": "Світшот з принтом",
                "slug": "svitshot-prynt",
                "description": "Світшот з модним принтом. Вільний крій.",
                "price": 1590,
                "discount_price": None,
                "category_slug": "svitshoty",
                "stock": 28,
                "gender": "U",
                "sizes": ["XS", "S", "M", "L", "XL"],
                "colors": ["Чорний", "Білий", "Сірий"],
                "image_url": "https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=600",
            },
            {
                "name": "Оверсайз світшот",
                "slug": "oversize-svitshot",
                "description": "Модний оверсайз світшот. Вільний крій.",
                "price": 2090,
                "discount_price": 1690,
                "category_slug": "svitshoty",
                "stock": 22,
                "gender": "U",
                "sizes": ["M", "L", "XL", "XXL"],
                "colors": ["Сірий", "Рожевий", "Синій"],
                "image_url": "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=600",
            },
            # ===== ПАЛЬТА =====
            {
                "name": "Шкіряна куртка бомбер",
                "slug": "shkiryana-kurtka-bomber",
                "description": "Стильна шкіряна куртка-бомбер. Вічна класика.",
                "price": 6890,
                "discount_price": 5490,
                "category_slug": "palta",
                "stock": 8,
                "gender": "U",
                "sizes": ["M", "L", "XL"],
                "colors": ["Чорний", "Сірий", "Коричневий"],
                "image_url": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=600",
            },
            {
                "name": "Пальто-оверсайз",
                "slug": "palto-oversize",
                "description": "Модне пальто оверсайз з вовни. Тепле, стильне.",
                "price": 4890,
                "discount_price": 3990,
                "category_slug": "palta",
                "stock": 15,
                "gender": "F",
                "sizes": ["S", "M", "L"],
                "colors": ["Бежевий", "Сірий", "Чорний"],
                "image_url": "https://images.unsplash.com/photo-1539533018447-63fcce2678e3?w=600",
            },
            {
                "name": "Парка",
                "slug": "parka",
                "description": "Тепла парка на зиму. Водовідштовхувальна тканина.",
                "price": 5290,
                "discount_price": 4490,
                "category_slug": "palta",
                "stock": 10,
                "gender": "U",
                "sizes": ["S", "M", "L", "XL", "XXL"],
                "colors": ["Оливковий", "Чорний", "Сірий"],
                "image_url": "https://images.unsplash.com/photo-1551537482-f2075a1d41f2?w=600",
            },
            # ===== ВЗУТТЯ =====
            {
                "name": "Кросівки червоні",
                "slug": "krosivky-bili",
                "description": "Класичні червоні кросівки. Універсальна модель.",
                "price": 2890,
                "discount_price": 2490,
                "category_slug": "vzuttya",
                "stock": 25,
                "gender": "U",
                "sizes": ["36", "37", "38", "39", "40", "41", "42", "43"],
                "colors": ["Білий"],
                "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600",
            },
            {
                "name": "Кросівки сині",
                "slug": "krosivky-chorni",
                "description": "Стильні сині кросівки на кожен день.",
                "price": 2990,
                "discount_price": None,
                "category_slug": "vzuttya",
                "stock": 30,
                "gender": "U",
                "sizes": ["37", "38", "39", "40", "41", "42", "43", "44"],
                "colors": ["Чорний"],
                "image_url": "https://images.unsplash.com/photo-1515955656352-a1fa3ffcd111?w=600",
            },
            # ===== ШОРТИ =====
            {
                "name": "Джинсові шорти",
                "slug": "dzhynsovi-shorty",
                "description": "Класичні джинсові шорти для літа.",
                "price": 1290,
                "discount_price": 990,
                "category_slug": "shorty",
                "stock": 35,
                "gender": "U",
                "sizes": ["S", "M", "L", "XL"],
                "colors": ["Синій", "Чорний"],
                "image_url": "https://images.unsplash.com/photo-1591195853828-11db59a44f6b?w=600",
            },
            # ===== АКСЕСУАРИ =====
            {
                "name": "Сумка шопер",
                "slug": "sumka-shoper",
                "description": "Містка сумка-шопер з натуральної шкіри.",
                "price": 3490,
                "discount_price": 2990,
                "category_slug": "aksesuary",
                "stock": 20,
                "gender": "F",
                "sizes": [],
                "colors": ["Чорний", "Бежевий", "Коричневий"],
                "image_url": "https://images.unsplash.com/photo-1590874103328-eac38a683ce7?w=600",
            },
            {
                "name": "Сонцезахисні окуляри",
                "slug": "soncezakhysni-okulyary",
                "description": "Стильні сонцезахисні окуляри.",
                "price": 1290,
                "discount_price": 990,
                "category_slug": "aksesuary",
                "stock": 45,
                "gender": "U",
                "sizes": [],
                "colors": ["Чорний", "Коричневий", "Золотий"],
                "image_url": "https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=600",
            },
            {
                "name": "Сорочка в клітинку",
                "slug": "sorochka-v-klinynku",
                "description": "Стильна сорочка в клітинку. Вільний крій.",
                "price": 1690,
                "discount_price": None,
                "category_slug": "sorochki",
                "stock": 35,
                "gender": "U",
                "sizes": ["S", "M", "L", "XL"],
                "colors": ["Червоний", "Синій", "Зелений"],
                "image_url": "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=600",
            },
            {
                "name": "Біла класична сорочка",
                "slug": "bila-sorochka-classic",
                "description": "Біла сорочка з бавовни 100%.",
                "price": 1490,
                "discount_price": 1190,
                "category_slug": "sorochki",
                "stock": 50,
                "gender": "U",
                "sizes": ["XS", "S", "M", "L", "XL"],
                "colors": ["Білий"],
                "image_url": "https://images.unsplash.com/photo-1598033129183-c4f50c736f10?w=600",
            },
        ]

        for prod_data in products_data:
            try:
                category = Category.objects.get(slug=prod_data["category_slug"])

                product, created = Product.objects.get_or_create(
                    slug=prod_data["slug"],
                    defaults={
                        "name": prod_data["name"],
                        "description": prod_data["description"],
                        "price": prod_data["price"],
                        "discount_price": prod_data["discount_price"],
                        "category": category,
                        "stock": prod_data["stock"],
                        "gender": prod_data["gender"],
                        "is_active": True,
                        "is_new": True if prod_data["discount_price"] else False,
                    },
                )

                if created:
                    # Додаємо зображення
                    if prod_data.get("image_url"):
                        img_content = self.download_image(
                            prod_data["image_url"], prod_data["slug"]
                        )
                        if img_content:
                            product.image.save(
                                f'{prod_data["slug"]}.jpg', img_content, save=True
                            )
                            self.stdout.write(
                                f"  📷 Додано зображення для {product.name}"
                            )

                    # Додаємо розміри
                    for size_name in prod_data["sizes"]:
                        try:
                            size = Size.objects.get(name=size_name)
                            product.sizes.add(size)
                        except Size.DoesNotExist:
                            pass

                    # Додаємо кольори
                    for color_name in prod_data["colors"]:
                        try:
                            color = Color.objects.get(name=color_name)
                            product.colors.add(color)
                        except Color.DoesNotExist:
                            if color_name == "Коричневий":
                                color = Color.objects.create(
                                    name=color_name, code="#8B4513"
                                )
                                product.colors.add(color)
                            elif color_name == "Золотий":
                                color = Color.objects.create(
                                    name=color_name, code="#FFD700"
                                )
                                product.colors.add(color)
                            elif color_name == "Оливковий":
                                color = Color.objects.create(
                                    name=color_name, code="#808000"
                                )
                                product.colors.add(color)

                    self.stdout.write(
                        self.style.SUCCESS(f"✅ Створено товар: {product.name}")
                    )
                else:
                    self.stdout.write(f"Товар вже існує: {product.name}")

            except Category.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f'Категорію {prod_data["category_slug"]} не знайдено'
                    )
                )

        self.stdout.write(self.style.SUCCESS("\n🎉 Всі товари успішно створені!"))
        self.stdout.write(f"📊 Всього товарів: {Product.objects.count()}")
        self.stdout.write(f"📂 Категорій: {Category.objects.count()}")
        self.stdout.write(f"🎨 Кольорів: {Color.objects.count()}")
        self.stdout.write(f"📏 Розмірів: {Size.objects.count()}")
