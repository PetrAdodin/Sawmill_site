from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Category

# Меню теперь содержит только пункты без аргументов
menu = [
    {'title': 'Главная', 'url_name': 'home'},
    {'title': 'О предприятии', 'url_name': 'about'},
]

# Тестовые данные товаров
posts_db = [
    {
        'id': 1,
        'title': 'Доска обрезная 25х100',
        'content': 'Доска обрезная, сорт 1, длина 6 м.',
        'is_published': True,
    },
    {
        'id': 2,
        'title': 'Брус 150х150',
        'content': 'Брус строганный, камерная сушка.',
        'is_published': True,
    },
    {
        'id': 3,
        'title': 'Вагонка штиль',
        'content': 'Липа, сорт Экстра, 14х96 мм.',
        'is_published': False,
    },
]

# Тестовые данные категорий
cats_db = [{'id': 1, 'name' : 'Доски'},
           {'id' : 2, 'name' : 'Горбыль'},
           {'id' : 3, 'name' : 'Брус'}]

def index(request):
    # Получаем все опубликованные товары из БД
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

def archive(request, year):
    if year > 2026:
        return redirect('home', permanent=True)
    return HttpResponse(f"<h1>Архив по годам</h1><p>{year}</p>")

def page_not_found(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена</h1>')
