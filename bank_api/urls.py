from django.urls import path
from . import views

urlpatterns = [
    path('exchange/<str:currencyFrom>/<str:amountFrom>/<str:currencyTo>', views.exchange),
    path('pay', views.pay),
    path('refund', views.refund),
]

