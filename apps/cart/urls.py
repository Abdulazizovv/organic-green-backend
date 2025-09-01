"""
URL configuration for Cart app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartViewSet, cart_info

# Create router for ViewSets
router = DefaultRouter()
router.register(r'cart', CartViewSet, basename='cart')

app_name = 'cart'

urlpatterns = [
    # Cart API info
    path('cart/', cart_info, name='cart-info'),
    
    # Cart routes
    path('', include(router.urls)),
]
