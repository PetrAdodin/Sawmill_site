from django.urls import path, register_converter

from lumber import converters
from lumber import views

register_converter(converters.FourDigitYearConverter, "year4")

urlpatterns = [
    path("", views.ProductHome.as_view(), name="home"),
    path("about/", views.AboutPage.as_view(), name="about"),
    path("addpage/", views.AddPage.as_view(), name="addpage"),
    path("addpage/raw/", views.AddPageRaw.as_view(), name="addpage_raw"),
    path("product/<slug:product_slug>/", views.ProductDetail.as_view(), name="product"),
    path("category/<slug:cat_slug>/", views.ProductCategory.as_view(), name="category"),
    path("tag/<slug:tag_slug>/", views.TagProductList.as_view(), name="tag"),
    path("edit/<slug:product_slug>/", views.UpdatePage.as_view(), name="edit_page"),
    path("delete/<slug:product_slug>/", views.DeletePage.as_view(), name="delete_page"),
    path("archive/<year4:year>/", views.ArchiveView.as_view(), name="archive"),
    path("demo/", views.DemoView.as_view(), name="demo"),
]