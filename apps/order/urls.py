"""
URL configuration for Order app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.order.views import OrderViewSet
from apps.order.info import order_info

# Create router for OrderViewSet
router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')

app_name = 'order'

urlpatterns = [
    # Order API info
    path('orders/info/', order_info, name='order-info'),
    
    # Order API routes
    path('', include(router.urls)),
]
