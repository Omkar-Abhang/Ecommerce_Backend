from django.shortcuts import render
from rest_framework import serializers


# Create your views here.
# Example inside your order status update view

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def update_order_status(order, new_status):
    order.status = new_status
    order.save()

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{order.user.id}",  # Send to user's group
        {
            'type': 'order_status_update',
            'order_id': order.id,
            'status': order.status,
        }
    )

# orders/views.py

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Cart, CartItem
from .serializer import CartSerializer, CartItemSerializer
from products.models import Product

class CartView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartSerializer

    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart

class AddToCartView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartItemSerializer

    def post(self, request, *args, **kwargs):
        cart, created = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get('product')
        quantity = request.data.get('quantity', 1)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += int(quantity)
        else:
            cart_item.quantity = int(quantity)
        cart_item.save()

        return Response(CartItemSerializer(cart_item).data, status=status.HTTP_201_CREATED)

class RemoveFromCartView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

    def get_queryset(self):
        return self.queryset.filter(cart__user=self.request.user)

from .models import Order, OrderItem, Cart, CartItem
from products.models import Product
from .serializer import OrderSerializer
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class PlaceOrderView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        cart = Cart.objects.filter(user=request.user).first()
        if not cart or cart.items.count() == 0:
            return Response({'error': 'Your cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

        total_price = 0
        for item in cart.items.all():
            total_price += item.product.price * item.quantity

        order = Order.objects.create(user=request.user, total_price=total_price)

        for item in cart.items.all():
            if item.product.stock < item.quantity:
                return Response({'error': f"Product {item.product.name} doesn't have enough stock."}, status=status.HTTP_400_BAD_REQUEST)
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            # Decrease stock
            item.product.stock -= item.quantity
            item.product.save()

        # Clear Cart after placing order
        cart.items.all().delete()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

class UpdateOrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']

class UpdateOrderStatusView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = Order.objects.all()
    serializer_class = UpdateOrderStatusSerializer

    def perform_update(self, serializer):
        order = serializer.save()

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
        'broadcast',  # <<< change group name to 'broadcast'
        {
            'type': 'order_status_update',
            'order_id': order.id,
            'status': order.status,
        }
    )