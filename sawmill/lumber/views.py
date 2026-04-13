from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Category, Tag

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