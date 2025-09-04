"""
URL configuration for API app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)
from api.views import (
    # Authentication views
    SimpleUserRegistrationView,
    UserRegistrationView,
    UserLoginView,
    CustomTokenObtainPairView,
    UserProfileView,
    ChangePasswordView,
    UserLogoutView,
    AvatarUploadView,
    DeleteAvatarView,
    VerifyAccountView,
    UserStatsView,
    check_auth_status,
    auth_info,
    # Product views
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
    path('auth/', auth_info, name='auth-info'),
    path('auth/register/simple/', SimpleUserRegistrationView.as_view(), name='auth-register-simple'),
    path('auth/register/', UserRegistrationView.as_view(), name='auth-register'),
    path('auth/login/', UserLoginView.as_view(), name='auth-login'),
    path('auth/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    # User Profile Management
    path('auth/profile/', UserProfileView.as_view(), name='user_profile'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('auth/upload-avatar/', AvatarUploadView.as_view(), name='upload_avatar'),
    path('auth/delete-avatar/', DeleteAvatarView.as_view(), name='delete_avatar'),
    path('auth/verify/', VerifyAccountView.as_view(), name='verify_account'),
    path('auth/stats/', UserStatsView.as_view(), name='user_stats'),
    path('auth/logout/', UserLogoutView.as_view(), name='user_logout'),
    path('auth/status/', check_auth_status, name='auth-status'),
    
    # API routes
    path('', include(router.urls)),
    
    # Cart API
    path('', include('apps.cart.urls')),
    
    # Favorites API
    path('', include('apps.favorites.urls')),
    
    # Order API
    path('', include('apps.order.urls')),
    
    # API Auth (for browsable API)
    path('auth/', include('rest_framework.urls')),
]
