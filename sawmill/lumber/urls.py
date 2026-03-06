from django.urls import path, re_path, register_converter
from lumber import views
from lumber import converters

register_converter(converters.FourDigitYearConverter, "year4")

urlpatterns = [
    path('lumber/', views.index),
    path('', views.index),
    path('cats/<int:cat_id>/', views.catigories),
    path('cats/<slug:cat_slug>/', views.catigories_by_slug),
    path('archive/<year4:year>/', views.archive),
]
