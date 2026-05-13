import uuid
from pathlib import Path

from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, F, Value, Count, Sum, Avg, Max, Min
from django.db.models.functions import Length

from .forms import ProductAddForm, ProductRawAddForm, UploadFileForm
from .models import Product, Category, Tag, Supplier, UploadedFile


menu = [
    {"title": "Главная", "url_name": "home"},
    {"title": "О предприятии", "url_name": "about"},
    {"title": "Добавить товар", "url_name": "addpage"},
    {"title": "Ручная форма", "url_name": "addpage_raw"},
]


def handle_uploaded_file(uploaded_file):
    """
    Сохраняет загруженный файл в MEDIA_ROOT/uploads со случайным именем.

    Случайное имя создаётся через uuid4, поэтому файлы с одинаковыми
    исходными именами не перезаписывают друг друга.
    """

    upload_dir = Path(settings.MEDIA_ROOT) / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)

    original_name = Path(uploaded_file.name)
    extension = original_name.suffix
    safe_stem = original_name.stem.replace(" ", "_")
    random_name = f"{safe_stem}_{uuid.uuid4().hex}{extension}"
    destination_path = upload_dir / random_name

    with open(destination_path, "wb+") as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)

    return destination_path


def index(request):
    posts = Product.published.all().select_related("category")

    context = {
        "title": "Главная страница",
        "menu": menu,
        "posts": posts,
    }

    return render(request, "lumber/index.html", context)


def about(request):
    upload_message = None

    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)

        if form.is_valid():
            uploaded_file = form.cleaned_data["file"]
            saved_path = handle_uploaded_file(uploaded_file)

            UploadedFile.objects.create(
                file=f"uploads/{saved_path.name}",
                original_name=uploaded_file.name,
            )

            upload_message = f"Файл «{uploaded_file.name}» успешно загружен."
    else:
        form = UploadFileForm()

    context = {
        "title": "О предприятии",
        "menu": menu,
        "form": form,
        "upload_message": upload_message,
    }

    return render(request, "lumber/about.html", context)


def addpage_raw(request):
    """
    Добавление товара через форму, не связанную с моделью.

    Данные проходят стандартную и пользовательскую валидацию,
    а затем вручную сохраняются в модель Product.
    """

    if request.method == "POST":
        form = ProductRawAddForm(request.POST)

        if form.is_valid():
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

            return redirect("home")
    else:
        form = ProductRawAddForm()

    context = {
        "title": "Добавление товара через несвязанную форму",
        "menu": menu,
        "form": form,
        "form_description": "Форма forms.Form: поля описаны вручную, сохранение выполняется в представлении.",
    }

    return render(request, "lumber/addpage_raw.html", context)


def addpage(request):
    """
    Добавление товара через форму, связанную с моделью Product.

    Форма поддерживает загрузку изображения товара.
    """

    if request.method == "POST":
        form = ProductAddForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form = ProductAddForm()

    context = {
        "title": "Добавление товара",
        "menu": menu,
        "form": form,
        "form_description": "Форма forms.ModelForm: поля связаны с моделью Product, сохранение выполняется через form.save().",
    }

    return render(request, "lumber/addpage.html", context)


def show_post(request, product_slug):
    post = get_object_or_404(Product.published, slug=product_slug)

    context = {
        "title": post.title,
        "menu": menu,
        "post": post,
    }

    return render(request, "lumber/post.html", context)


def category_detail(request, cat_slug):
    category = get_object_or_404(Category, slug=cat_slug)
    posts = Product.published.filter(category=category).select_related("category")

    context = {
        "title": f"Категория: {category.name}",
        "menu": menu,
        "posts": posts,
        "cat_selected": category.id,
    }

    return render(request, "lumber/index.html", context)


def tag_detail(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)
    posts = tag.products.filter(is_published=Product.Status.PUBLISHED).select_related("category")

    context = {
        "title": f"Тег: {tag.name}",
        "menu": menu,
        "posts": posts,
        "tag_selected": tag.id,
    }

    return render(request, "lumber/index.html", context)


def archive(request, year):
    if year > 2026:
        return redirect("home", permanent=True)

    return HttpResponse(f"<h1>Архив по годам</h1><p>{year}</p>")


def page_not_found(request, exception):
    return HttpResponseNotFound("<h1>Страница не найдена</h1>")


def demo_queries(request):
    results = {}

    results["first_product"] = Product.objects.first()
    results["last_product"] = Product.objects.order_by("pk").last()

    results["latest_product"] = Product.objects.latest("time_update")
    results["earliest_product"] = Product.objects.earliest("time_update")

    try:
        prod = Product.objects.get(pk=2)
        results["prev_by_time"] = prod.get_previous_by_time_update()
        results["next_by_time"] = prod.get_next_by_time_update()
    except Product.DoesNotExist:
        results["prev_by_time"] = results["next_by_time"] = None

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

    context = {
        "title": "Демонстрация методов ORM",
        "menu": menu,
        "results": results,
    }

    return render(request, "lumber/demo.html", context)