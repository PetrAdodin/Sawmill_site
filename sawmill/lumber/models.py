from django.db import models
from django.urls import reverse
from django.core.validators import MinLengthValidator, MaxLengthValidator


# Менеджер для выборки только опубликованных товаров
class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_published=Product.Status.PUBLISHED)


# Модель категории
class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name="Категория")
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category', kwargs={'cat_slug': self.slug})


# Модель тега
class Tag(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name="Тег")
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tag', kwargs={'tag_slug': self.slug})


# Модель поставщика
class Supplier(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    contact_person = models.CharField(max_length=100, blank=True, verbose_name="Контактное лицо")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    email = models.EmailField(blank=True, verbose_name="E-mail")

    def __str__(self):
        return self.name


# Основная модель товара
class Product(models.Model):
    class Status(models.IntegerChoices):
        DRAFT = 0, 'Черновик'
        PUBLISHED = 1, 'Опубликовано'

    title = models.CharField(max_length=255, verbose_name="Название")
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL",
                            validators=[MinLengthValidator(5), MaxLengthValidator(100)])
    content = models.TextField(blank=True, verbose_name="Описание")
    photo = models.ImageField(upload_to="products/%Y/%m/%d/", blank=True, null=True, verbose_name="Фото")
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Цена")
    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    time_update = models.DateTimeField(auto_now=True, verbose_name="Время изменения")
    is_published = models.BooleanField(choices=Status.choices, default=Status.DRAFT, verbose_name="Статус")

    # Связи
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products', verbose_name="Категория")
    tags = models.ManyToManyField(Tag, blank=True, related_name='products', verbose_name="Теги")
    supplier = models.OneToOneField(Supplier, on_delete=models.SET_NULL, null=True, blank=True,
                                    verbose_name="Поставщик")

    # Менеджеры
    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['-time_create']
        indexes = [models.Index(fields=['-time_create'])]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('product', kwargs={'product_slug': self.slug})