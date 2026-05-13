from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.utils.deconstruct import deconstructible

from .models import Category, Product, Supplier, Tag


@deconstructible
class RussianProductTitleValidator:
    """
    Пользовательский валидатор для проверки названия товара.

    По тематике сайта название товара должно быть на русском языке.
    Разрешены русские буквы, цифры, пробелы, дефис, кавычки и некоторые
    знаки препинания, которые часто встречаются в названиях пиломатериалов:
    "Доска обрезная 40x150", "Брус строганый 100-150", "Вагонка сорт А".
    """

    allowed_chars = (
        "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЫЪЭЮЯ"
        "абвгдеёжзийклмнопрстуфхцчшщьыъэюя"
        "0123456789 -.,«»\"'()/xX×"
    )
    code = "russian_product_title"

    def __init__(self, message=None):
        self.message = (
            message
            or "Название товара должно содержать только русские буквы, цифры, пробелы и допустимые знаки."
        )

    def __call__(self, value):
        if not set(value) <= set(self.allowed_chars):
            raise ValidationError(
                self.message,
                code=self.code,
                params={"value": value},
            )


class ProductRawAddForm(forms.Form):
    """
    Форма добавления товара, НЕ связанная с моделью.

    Используется для выполнения первого пункта лабораторной работы:
    форма создаётся вручную через forms.Form, поля описываются отдельно,
    сохранение в БД выполняется в представлении.
    """

    title = forms.CharField(
        max_length=255,
        min_length=5,
        label="Название товара",
        validators=[RussianProductTitleValidator()],
        widget=forms.TextInput(
            attrs={
                "class": "form-input",
                "placeholder": "Например: Доска обрезная 40x150",
            }
        ),
        error_messages={
            "min_length": "Название товара слишком короткое. Минимум 5 символов.",
            "required": "Введите название товара.",
        },
    )

    slug = forms.SlugField(
        max_length=255,
        label="URL",
        validators=[
            MinLengthValidator(5, message="URL должен содержать минимум 5 символов."),
            MaxLengthValidator(100, message="URL должен содержать максимум 100 символов."),
        ],
        widget=forms.TextInput(
            attrs={
                "class": "form-input",
                "placeholder": "Например: doska-obreznaya-40x150",
            }
        ),
        error_messages={
            "required": "Введите URL товара.",
            "invalid": "URL может содержать только латинские буквы, цифры, дефисы и подчёркивания.",
        },
    )

    content = forms.CharField(
        required=False,
        label="Описание",
        widget=forms.Textarea(
            attrs={
                "class": "form-input",
                "cols": 50,
                "rows": 6,
                "placeholder": "Описание товара, порода древесины, влажность, сорт, назначение.",
            }
        ),
    )

    price = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        min_value=0,
        label="Цена",
        widget=forms.NumberInput(
            attrs={
                "class": "form-input",
                "placeholder": "Например: 12500.00",
                "step": "0.01",
            }
        ),
        error_messages={
            "invalid": "Введите корректную цену.",
            "min_value": "Цена не может быть отрицательной.",
        },
    )

    is_published = forms.BooleanField(
        required=False,
        initial=True,
        label="Опубликовать товар",
    )

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label="Категория не выбрана",
        label="Категория",
        widget=forms.Select(attrs={"class": "form-input"}),
        error_messages={
            "required": "Выберите категорию товара.",
        },
    )

    supplier = forms.ModelChoiceField(
        queryset=Supplier.objects.all(),
        required=False,
        empty_label="Поставщик не выбран",
        label="Поставщик",
        widget=forms.Select(attrs={"class": "form-input"}),
    )

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        label="Теги",
        widget=forms.SelectMultiple(attrs={"class": "form-input"}),
    )


class ProductAddForm(forms.ModelForm):
    """
    Форма добавления товара, связанная с моделью Product.

    Используется для второго и четвёртого пунктов лабораторной работы:
    форма строится на основе модели, поддерживает загрузку изображения
    товара и сохраняет запись через form.save().
    """

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        empty_label="Категория не выбрана",
        label="Категория",
        widget=forms.Select(attrs={"class": "form-input"}),
    )

    supplier = forms.ModelChoiceField(
        queryset=Supplier.objects.all(),
        required=False,
        empty_label="Поставщик не выбран",
        label="Поставщик",
        widget=forms.Select(attrs={"class": "form-input"}),
    )

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        label="Теги",
        widget=forms.SelectMultiple(attrs={"class": "form-input"}),
    )

    class Meta:
        model = Product
        fields = [
            "title",
            "slug",
            "content",
            "photo",
            "price",
            "is_published",
            "category",
            "supplier",
            "tags",
        ]

        labels = {
            "title": "Название товара",
            "slug": "URL",
            "content": "Описание",
            "photo": "Фото товара",
            "price": "Цена",
            "is_published": "Статус публикации",
        }

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Например: Брус строганый 100x100",
                }
            ),
            "slug": forms.TextInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Например: brus-stroganyy-100x100",
                }
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "form-input",
                    "cols": 50,
                    "rows": 6,
                    "placeholder": "Описание товара, характеристики и область применения.",
                }
            ),
            "photo": forms.ClearableFileInput(
                attrs={
                    "class": "form-input",
                }
            ),
            "price": forms.NumberInput(
                attrs={
                    "class": "form-input",
                    "placeholder": "Например: 9800.00",
                    "step": "0.01",
                }
            ),
        }

        error_messages = {
            "title": {
                "required": "Введите название товара.",
                "max_length": "Название товара слишком длинное.",
            },
            "slug": {
                "required": "Введите URL товара.",
                "unique": "Товар с таким URL уже существует.",
                "invalid": "URL может содержать только латинские буквы, цифры, дефисы и подчёркивания.",
            },
            "category": {
                "required": "Выберите категорию товара.",
            },
        }

    def clean_title(self):
        title = self.cleaned_data["title"]

        validator = RussianProductTitleValidator()
        validator(title)

        if len(title) > 50:
            raise ValidationError("Длина названия товара не должна превышать 50 символов.")

        return title


class UploadFileForm(forms.Form):
    """
    Форма загрузки произвольного файла на сервер.

    Используется для третьего пункта лабораторной работы.
    Файл сохраняется вручную в представлении со случайным именем.
    """

    file = forms.FileField(
        label="Файл",
        widget=forms.ClearableFileInput(attrs={"class": "form-input"}),
        error_messages={
            "required": "Выберите файл для загрузки.",
        },
    )