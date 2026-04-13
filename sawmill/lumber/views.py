from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, F, Value, Count, Sum, Avg, Max, Min
from django.db.models.functions import Length
from .models import Product, Category, Tag, Supplier

menu = [
    {'title': 'Главная', 'url_name': 'home'},
    {'title': 'О предприятии', 'url_name': 'about'},
]

def index(request):
    posts = Product.published.all().select_related('category')
    context = {
        'title': 'Главная страница',
        'menu': menu,
        'posts': posts,
    }
    return render(request, 'lumber/index.html', context)

def about(request):
    context = {
        'title': 'О предприятии',
        'menu': menu,
    }
    return render(request, 'lumber/about.html', context)

def show_post(request, product_slug):
    post = get_object_or_404(Product.published, slug=product_slug)
    context = {
        'title': post.title,
        'menu': menu,
        'post': post,
    }
    return render(request, 'lumber/post.html', context)

def category_detail(request, cat_slug):
    category = get_object_or_404(Category, slug=cat_slug)
    posts = Product.published.filter(category=category).select_related('category')
    context = {
        'title': f'Категория: {category.name}',
        'menu': menu,
        'posts': posts,
        'cat_selected': category.id,
    }
    return render(request, 'lumber/index.html', context)

def tag_detail(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)
    posts = tag.products.filter(is_published=Product.Status.PUBLISHED).select_related('category')
    context = {
        'title': f'Тег: {tag.name}',
        'menu': menu,
        'posts': posts,
        'tag_selected': tag.id,
    }
    return render(request, 'lumber/index.html', context)

def archive(request, year):
    if year > 2026:
        return redirect('home', permanent=True)
    return HttpResponse(f"<h1>Архив по годам</h1><p>{year}</p>")

def page_not_found(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена</h1>')

# Демонстрация различных методов ORM
def demo_queries(request):
    results = {}

    # 1. first(), last()
    results['first_product'] = Product.objects.first()
    results['last_product'] = Product.objects.order_by('pk').last()

    # 2. latest(), earliest() по полю time_update
    results['latest_product'] = Product.objects.latest('time_update')
    results['earliest_product'] = Product.objects.earliest('time_update')

    # 3. get_previous_by_ и get_next_by_ (на примере продукта с id=2)
    try:
        prod = Product.objects.get(pk=2)
        results['prev_by_time'] = prod.get_previous_by_time_update()
        results['next_by_time'] = prod.get_next_by_time_update()
    except Product.DoesNotExist:
        results['prev_by_time'] = results['next_by_time'] = None

    # 4. exists() и count()
    results['cat_exists'] = Category.objects.filter(slug='wood').exists()
    results['products_count'] = Product.objects.count()

    # 5. Класс Q (OR, AND, NOT)
    q_products = Product.objects.filter(Q(price__gt=1000) | Q(category__name__icontains='пиломатериалы'))
    results['q_or_products'] = list(q_products)
    q_and_products = Product.objects.filter(Q(price__lt=500) & Q(is_published=Product.Status.PUBLISHED))
    results['q_and_products'] = list(q_and_products)
    q_not_products = Product.objects.filter(~Q(category__name='Доска'))
    results['q_not_products'] = list(q_not_products)

    # 6. Класс F (сравнение поля с другим полем)
    # Например, товары, у которых id больше, чем price (условно, для демонстрации)
    f_products = Product.objects.filter(id__gt=F('price'))
    results['f_products'] = list(f_products)

    # 7. Класс Value в annotate() (вычисляемое поле)
    suppliers = Supplier.objects.annotate(is_active=Value(True))
    results['annotated_suppliers'] = suppliers

    # 8. Агрегирующие функции (Min, Max, Sum, Avg, Count)
    results['min_price'] = Product.objects.aggregate(Min('price'))
    results['max_price'] = Product.objects.aggregate(Max('price'))
    results['sum_price'] = Product.objects.aggregate(Sum('price'))
    results['avg_price'] = Product.objects.aggregate(Avg('price'))
    results['total_products'] = Product.objects.aggregate(total=Count('id'))

    # 9. Группировка записей (values + annotate)
    # Количество товаров в каждой категории
    cat_group = Category.objects.annotate(total_products=Count('products')).filter(total_products__gt=0)
    results['grouped_categories'] = cat_group
    # Количество товаров по каждому тегу
    tag_group = Tag.objects.annotate(total_products=Count('products')).filter(total_products__gt=0)
    results['grouped_tags'] = tag_group

    # 10. Вычисления на стороне СУБД (функция Length)
    products_with_name_len = Product.objects.annotate(title_len=Length('title')).values('title', 'title_len')
    results['title_lengths'] = list(products_with_name_len[:5])

    context = {
        'title': 'Демонстрация методов ORM',
        'menu': menu,
        'results': results,
    }
    return render(request, 'lumber/demo.html', context)

