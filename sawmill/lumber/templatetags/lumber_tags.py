from django import template
from lumber.models import Category, Tag

register = template.Library()

@register.inclusion_tag('lumber/list_categories.html')
def show_categories():
    cats = Category.objects.all()
    return {"cats": cats}

@register.inclusion_tag('lumber/list_tags.html')
def show_all_tags():
    tags = Tag.objects.all()
    return {"tags": tags}