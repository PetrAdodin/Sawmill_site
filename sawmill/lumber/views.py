import uuid
from datetime import date
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.db.models import Avg, Count, F, Max, Min, Q, Sum, Value
from django.db.models.functions import Length
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import CreateView, DeleteView, FormView, UpdateView

from .forms import ProductAddForm, ProductRawAddForm, UploadFileForm
from .models import Category, Product, Supplier, Tag, UploadedFile
from .utils import DataMixin


def handle_uploaded_file(uploaded_file):
    """
    Сохраняет загруженный файл в MEDIA_ROOT/uploads со случайным именем.
    Файлы с одинаковыми исходными именами не перезаписывают друг друга.
    """
    upload_dir = Path(settings.MEDIA_ROOT) / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)

    original_name = Path(uploaded_file.name)
    random_name = f"{original_name.stem.replace(' ', '_')}_{uuid.uuid4().hex}{original_name.suffix}"
    destination_path = upload_dir / random_name

    with open(destination_path, "wb+") as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)

    return destination_path


class ProductHome(DataMixin, ListView):
    model = Product
    template_name = "lumber/index.html"
    context_object_name = "posts"
    title_page = "Главная страница"

    def get_queryset(self):
        return (
            Product.published.all()
            .select_related("category", "supplier")
            .prefetch_related("tags")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context, cat_selected=0)


class ProductCategory(DataMixin, ListView):
    template_name = "lumber/index.html"
    context_object_name = "posts"
    allow_empty = False

    def get_queryset(self):
        return (
            Product.published.filter(category__slug=self.kwargs["cat_slug"])
            .select_related("category", "supplier")
            .prefetch_related("tags")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = context["posts"][0].category
        return self.get_mixin_context(
            context,
            title=f"Категория - {category.name}",
            cat_selected=category.id,
        )


class TagProductList(DataMixin, ListView):
    template_name = "lumber/index.html"
    context_object_name = "posts"
    allow_empty = False

    def get_queryset(self):
        tag = get_object_or_404(Tag, slug=self.kwargs["tag_slug"])
        return (
            tag.products.filter(is_published=Product.Status.PUBLISHED)
            .select_related("category", "supplier")
            .prefetch_related("tags")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = get_object_or_404(Tag, slug=self.kwargs["tag_slug"])
        return self.get_mixin_context(
            context,
            title=f"Тег: {tag.name}",
            tag_selected=tag.id,
        )


class ProductDetail(DataMixin, DetailView):
    model = Product
    template_name = "lumber/post.html"
    context_object_name = "post"
    slug_url_kwarg = "product_slug"

    def get_object(self, queryset=None):
        return get_object_or_404(
            Product.published.select_related("category", "supplier").prefetch_related("tags"),
            slug=self.kwargs[self.slug_url_kwarg],
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(
            context,
            title=context["post"].title,
            cat_selected=context["post"].category_id,
        )


class AboutPage(DataMixin, FormView):
    form_class = UploadFileForm
    template_name = "lumber/about.html"
    success_url = reverse_lazy("about")
    title_page = "О предприятии"

    def form_valid(self, form):
        uploaded_file = form.cleaned_data["file"]
        saved_path = handle_uploaded_file(uploaded_file)
        UploadedFile.objects.create(
            file=f"uploads/{saved_path.name}",
            original_name=uploaded_file.name,
        )
        messages.success(self.request, f"Файл «{uploaded_file.name}» успешно загружен.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(
            context,
            button_text="Отправить",
        )


class AddPageRaw(DataMixin, FormView):
    form_class = ProductRawAddForm
    template_name = "lumber/addpage_raw.html"
    success_url = reverse_lazy("home")
    title_page = "Добавление товара через несвязанную форму"

    def form_valid(self, form):
        product = Product.objects.create(
            title=form.cleaned_data["title"],
            slug=form.cleaned_data["slug"],
            content=form.cleaned_data["content"],
            price=form.cleaned_data["price"],
            is_published=form.cleaned_data["is_published"],
            category=form.cleaned_data["category"],
            supplier=form.cleaned_data["supplier"],
        )
        product.tags.set(form.cleaned_data["tags"])
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(
            context,
            form_description="Форма forms.Form: поля описаны вручную, а сохранение выполняется прямо в представлении.",
            button_text="Добавить товар",
        )


class AddPage(DataMixin, CreateView):
    form_class = ProductAddForm
    template_name = "lumber/addpage.html"
    success_url = reverse_lazy("home")
    title_page = "Добавление товара"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(
            context,
            form_description="Форма forms.ModelForm: поля связаны с моделью Product, сохранение выполняется через form.save().",
            button_text="Добавить товар",
        )


class UpdatePage(DataMixin, UpdateView):
    model = Product
    form_class = ProductAddForm
    template_name = "lumber/addpage.html"
    success_url = reverse_lazy("home")
    slug_url_kwarg = "product_slug"
    title_page = "Редактирование товара"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(
            context,
            form_description="Форма редактирования товара. После сохранения запись обновляется в базе данных.",
            button_text="Сохранить изменения",
        )


class DeletePage(DataMixin, DeleteView):
    model = Product
    template_name = "lumber/product_confirm_delete.html"
    success_url = reverse_lazy("home")
    slug_url_kwarg = "product_slug"
    context_object_name = "post"
    title_page = "Удаление товара"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return self.get_mixin_context(context)


class DemoView(DataMixin, TemplateView):
    template_name = "lumber/demo.html"
    title_page = "Демонстрация методов ORM"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        results = {}
        results["first_product"] = Product.objects.first()
        results["last_product"] = Product.objects.order_by("pk").last()
        results["latest_product"] = Product.objects.order_by("-time_update").first()
        results["earliest_product"] = Product.objects.order_by("time_update").first()

        try:
            prod = Product.objects.get(pk=2)
            results["prev_by_time"] = prod.get_previous_by_time_update()
            results["next_by_time"] = prod.get_next_by_time_update()
        except Product.DoesNotExist:
            results["prev_by_time"] = None
            results["next_by_time"] = None

        results["cat_exists"] = Category.objects.filter(slug="wood").exists()
        results["products_count"] = Product.objects.count()

        q_products = Product.objects.filter(
            Q(price__gt=1000) | Q(category__name__icontains="пиломатериалы")
        )
        results["q_or_products"] = list(q_products)

        q_and_products = Product.objects.filter(
            Q(price__lt=500) & Q(is_published=Product.Status.PUBLISHED)
        )
        results["q_and_products"] = list(q_and_products)

        q_not_products = Product.objects.filter(~Q(category__name="Доска"))
        results["q_not_products"] = list(q_not_products)

        f_products = Product.objects.filter(id__gt=F("price"))
        results["f_products"] = list(f_products)

        suppliers = Supplier.objects.annotate(is_active=Value(True))
        results["annotated_suppliers"] = suppliers

        results["min_price"] = Product.objects.aggregate(Min("price"))
        results["max_price"] = Product.objects.aggregate(Max("price"))
        results["sum_price"] = Product.objects.aggregate(Sum("price"))
        results["avg_price"] = Product.objects.aggregate(Avg("price"))
        results["total_products"] = Product.objects.aggregate(total=Count("id"))

        cat_group = Category.objects.annotate(total_products=Count("products")).filter(
            total_products__gt=0
        )
        results["grouped_categories"] = cat_group

        tag_group = Tag.objects.annotate(total_products=Count("products")).filter(
            total_products__gt=0
        )
        results["grouped_tags"] = tag_group

        products_with_name_len = Product.objects.annotate(title_len=Length("title")).values(
            "title",
            "title_len",
        )
        results["title_lengths"] = list(products_with_name_len[:5])

        return self.get_mixin_context(context, results=results)


class ArchiveView(View):
    def get(self, request, year):
        if year > date.today().year:
            return redirect("home", permanent=True)
        return HttpResponse(
            f"""
            <h1>Архив по годам</h1>
            <p>Год: {year}</p>
            """
        )


def page_not_found(request, exception):
    return HttpResponseNotFound(
        """
        <h1>Страница не найдена</h1>
        """
    )