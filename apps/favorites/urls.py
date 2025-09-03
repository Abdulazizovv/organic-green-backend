"""
URL configuration for Favorites app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FavoriteViewSet, favorites_info

# Create router for ViewSets
router = DefaultRouter()
router.register(r'favorites', FavoriteViewSet, basename='favorite')

app_name = 'favorites'

urlpatterns = [
    # Favorites API info
    path('favorites/info/', favorites_info, name='favorites-info'),
    
    # Favorites routes
    path('', include(router.urls)),
]
