from django.urls import path, include
from bank_api import urls as bank_urls
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('bank/', include(bank_urls)),
]
