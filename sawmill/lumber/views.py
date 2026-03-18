from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import render, redirect, get_object_or_404

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

def index(request):
    # Отбираем только опубликованные товары
    posts = [p for p in posts_db if p['is_published']]
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

def show_post(request, post_id):
    """Страница отдельного товара"""
    # Ищем товар по id (упрощённо, без БД)
    post = next((p for p in posts_db if p['id'] == post_id), None)
    if not post:
        raise Http404("Товар не найден")
    context = {
        'title': post['title'],
        'menu': menu,
        'post': post,
    }
    return render(request, 'lumber/post.html', context)

# Остальные функции (catigories, archive и т.д.) остаются без изменений
def catigories(request, cat_id):
    return HttpResponse(f"<h1>Пиломатериал по категориям</h1><p>id: {cat_id}</p>")

def catigories_by_slug(request, cat_slug):
    return HttpResponse(f"<h1>Пиломатериал по категориям</h1><p>slug:{cat_slug}</p>")

def archive(request, year):
    if year > 2026:
        return redirect('home', permanent=True)
    return HttpResponse(f"<h1>Архив по годам</h1><p>{year}</p>")

def page_not_found(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена</h1>')
