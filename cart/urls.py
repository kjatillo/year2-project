from django.urls import path
from . import views

app_name='cart'

urlpatterns = [
    path('add/<uuid:service_id>/', views.add_cart, name='add_cart'),
    path('', views.cart_detail, name='cart_detail'),
    path('full_remove/<uuid:service_id>/', views.full_remove, name='full_remove'),
]
