from django.contrib import admin
from django.contrib import messages
from django.db.models import Count
from django.utils.html import format_html

from .models import Product, Category, Tag, Supplier, UploadedFile


class HasSupplierFilter(admin.SimpleListFilter):
    title = "Наличие поставщика"
    parameter_name = "supplier_status"

    def lookups(self, request, model_admin):
        return [
            ("yes", "Есть поставщик"),
            ("no", "Нет поставщика"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(supplier__isnull=False)

        if self.value() == "no":
            return queryset.filter(supplier__isnull=True)

        return queryset


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")
    list_display_links = ("id", "name")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")
    list_display_links = ("id", "name")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "contact_person", "phone", "email")
    list_display_links = ("id", "name")
    search_fields = ("name", "contact_person")


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ("id", "original_name", "file", "uploaded_at")
    list_display_links = ("id", "original_name")
    readonly_fields = ("uploaded_at",)
    search_fields = ("original_name",)
    ordering = ("-uploaded_at",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "post_photo",
        "category",
        "price",
        "is_published",
        "time_create",
        "supplier_info",
    )
    list_display_links = ("title",)
    list_editable = ("is_published",)
    ordering = ("-time_create", "title")
    list_per_page = 10

    search_fields = ("title", "category__name", "content")

    list_filter = (HasSupplierFilter, "category", "is_published", "tags")

    fields = [
        "title",
        "slug",
        "category",
        "tags",
        "supplier",
        "price",
        "content",
        "photo",
        "post_photo",
        "is_published",
        "time_create",
        "time_update",
    ]
    readonly_fields = ["post_photo", "time_create", "time_update"]
    filter_horizontal = ["tags"]
    prepopulated_fields = {"slug": ("title",)}
    save_on_top = True

    @admin.display(description="Изображение")
    def post_photo(self, obj: Product):
        if obj.photo:
            return format_html(
                '<img src="{}" width="70" style="border-radius: 6px;" />',
                obj.photo.url,
            )

        return "Без фото"

    @admin.display(description="Краткое описание", ordering="content")
    def brief_info(self, obj: Product):
        if obj.content:
            return f"{obj.content[:50]}..." if len(obj.content) > 50 else obj.content

        return "Нет описания"

    @admin.display(description="Поставщик")
    def supplier_info(self, obj: Product):
        return obj.supplier.name if obj.supplier else "—"

    @admin.action(description="Опубликовать выбранные товары")
    def make_published(self, request, queryset):
        count = queryset.update(is_published=Product.Status.PUBLISHED)
        self.message_user(request, f"Опубликовано {count} товаров.", messages.SUCCESS)

    @admin.action(description="Снять с публикации выбранные товары")
    def make_draft(self, request, queryset):
        count = queryset.update(is_published=Product.Status.DRAFT)
        self.message_user(request, f"Снято с публикации {count} товаров.", messages.WARNING)

    @admin.action(description="Показать количество товаров в категориях")
    def show_category_stats(self, request, queryset):
        stats = Category.objects.annotate(total=Count("products")).values("name", "total")
        message = "Статистика по категориям: " + ", ".join(
            [f"{s['name']}: {s['total']}" for s in stats]
        )
        self.message_user(request, message, messages.INFO)

    actions = ["make_published", "make_draft", "show_category_stats"]