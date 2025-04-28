# orders/urls.py

from django.urls import path
from .views import CartView, AddToCartView, RemoveFromCartView, PlaceOrderView, UpdateOrderStatusView

urlpatterns = [
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/', AddToCartView.as_view(), name='add_to_cart'),
    path('cart/remove/<int:pk>/', RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('place-order/', PlaceOrderView.as_view(), name='place_order'),
    path('update-order/<int:pk>/', UpdateOrderStatusView.as_view(), name='update_order'),
]
