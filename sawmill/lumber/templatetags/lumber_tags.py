from django import template
from lumber.models import Category

register = template.Library()

@register.inclusion_tag('lumber/list_categories.html')
def show_categories():
    cats = Category.objects.all()
    return {"cats": cats}