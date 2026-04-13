from django.urls import path, register_converter
from lumber import views
from lumber import converters

register_converter(converters.FourDigitYearConverter, "year4")

urlpatterns = [
    path('', views.index, name='home'),
    path('about/', views.about, name='about'),
    path('product/<slug:product_slug>/', views.show_post, name='product'),
    path('category/<slug:cat_slug>/', views.category_detail, name='category'),
    path('tag/<slug:tag_slug>/', views.tag_detail, name='tag'),
]