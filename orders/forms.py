from django import forms
from .models import Order


class OrderCreateForm(forms.ModelForm):
    """Форма оформлення замовлення"""

    # Додаткове поле для пароля (для неавторизованих)
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        required=False,
        help_text="Залиште порожнім, якщо не хочете встановлювати пароль",
    )

    class Meta:
        model = Order
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "address",
            "city",
            "postal_code",
            "delivery_method",
            "payment_method",
            "comment",
        ]
        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ім'я"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Прізвище"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "example@mail.com"}
            ),
            "phone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+380 XX XXX XXXX"}
            ),
            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Вулиця, будинок, квартира",
                }
            ),
            "city": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Місто"}
            ),
            "postal_code": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Поштовий індекс"}
            ),
            "delivery_method": forms.Select(attrs={"class": "form-select"}),
            "payment_method": forms.Select(attrs={"class": "form-select"}),
            "comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Додаткові побажання...",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        self.fields["email"].required = True
        self.fields["phone"].required = True
        self.fields["address"].required = True
        self.fields["city"].required = True

    def clean_phone(self):
        """Валідація телефону"""
        phone = self.cleaned_data.get("phone")
        # Проста валідація українського номера
        if (
            phone
            and not phone.replace("+", "").replace(" ", "").replace("-", "").isdigit()
        ):
            raise forms.ValidationError("Введіть коректний номер телефону")
        return phone

    def clean_email(self):
        """Валідація email"""
        email = self.cleaned_data.get("email")
        if email and "@" not in email:
            raise forms.ValidationError("Введіть коректний email")
        return email
