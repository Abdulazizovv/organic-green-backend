"""
URL configuration for API app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from .views import (
    ProductViewSet,
    ProductCategoryViewSet,
    ProductTagViewSet,
    api_health_check,
    api_documentation,
)

# Create router for ViewSets
router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', ProductCategoryViewSet, basename='category')
router.register(r'tags', ProductTagViewSet, basename='tag')

app_name = 'api'

urlpatterns = [
    # API Documentation and Health
    path('', api_documentation, name='api-documentation'),
    path('health/', api_health_check, name='api-health'),
    
    # Authentication endpoints
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # API routes
    path('', include(router.urls)),
    
    # API Auth (for browsable API)
    path('auth/', include('rest_framework.urls')),
]
