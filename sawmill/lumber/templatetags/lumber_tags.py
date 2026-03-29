from django import template
import lumber.views as views
from lumber.models import Category

register = template.Library()

@register.simple_tag()
def get_categories():
    return views.cats_db

@register.inclusion_tag('lumber/list_categories.html')
def show_categories():
    cats = Category.objects.all()
    return {"cats": cats}