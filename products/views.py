# products/views.py

from rest_framework.response import Response
from rest_framework import viewsets, permissions
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from django.core.cache import cache  
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allow only admins to create/update/delete, others can only read
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

    def list(self, request, *args, **kwargs):
        cached_categories = cache.get('categories')
        if cached_categories:
            return Response(cached_categories)

        response = super().list(request, *args, **kwargs)
        cache.set('categories', response.data, timeout=3600)  # Cache for 1 hour
        return response

    def perform_create(self, serializer):
        cache.delete('categories')  # Invalidate cache
        serializer.save()

    def perform_update(self, serializer):
        cache.delete('categories')
        serializer.save()

    def perform_destroy(self, instance):
        cache.delete('categories')
        instance.delete()


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'stock']  # Category ID and stock availability
    search_fields = ['name', 'description']  # Optional: search by name/description
    ordering_fields = ['price', 'stock']  # Optional: sort by price or stock

    def list(self, request, *args, **kwargs):
        cached_products = cache.get('products')
        if cached_products and not request.query_params:
            return Response(cached_products)

        response = super().list(request, *args, **kwargs)
        if not request.query_params:
            cache.set('products', response.data, timeout=3600)
        return response

    def perform_create(self, serializer):
        cache.delete('products')
        serializer.save()

    def perform_update(self, serializer):
        cache.delete('products')
        serializer.save()

    def perform_destroy(self, instance):
        cache.delete('products')
        instance.delete()