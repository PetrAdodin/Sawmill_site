from django.urls import path, register_converter
from lumber import views
from lumber import converters

register_converter(converters.FourDigitYearConverter, "year4")

urlpatterns = [
    path('', views.index, name='home'),
    path('about/', views.about, name='about'),
    path('post/<int:post_id>/', views.show_post, name='post'),  # новый маршрут
    path('cats/<int:cat_id>/', views.catigories, name='cats'),
    path('cats/<slug:cat_slug>/', views.catigories_by_slug, name='cats_slug'),
    path('archive/<year4:year>/', views.archive, name='archive'),
]
