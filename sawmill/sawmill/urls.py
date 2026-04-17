from django.contrib import admin
from django.urls import path, include
from lumber.views import page_not_found

# Настройка заголовков админ-панели
admin.site.site_header = "Панель администрирования"
admin.site.index_title = "Управление товарами и категориями"

handler404 = page_not_found

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('lumber.urls')),
]

