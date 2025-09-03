"""
Views for Favorites API
Professional-grade views for favorites/wishlist functionality
"""
from rest_framework import generics, viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count, Avg, F
from django.shortcuts import get_object_or_404
from django.db import transaction
from apps.products.models import Product
from apps.favorites.models import Favorite
from apps.favorites.serializers import (
    FavoriteSerializer, AddToFavoritesSerializer, 
    FavoriteCheckSerializer, FavoriteStatsSerializer
)
import logging

logger = logging.getLogger(__name__)


class FavoritePagination(PageNumberPagination):
    """Custom pagination for favorites"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class FavoriteViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user favorites
    
    Provides CRUD operations for user's favorite products (wishlist)
    """
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = FavoritePagination
    
    def get_queryset(self):
        """
        Get favorites for the authenticated user only
        """
        return Favorite.objects.filter(
            user=self.request.user
        ).select_related('product', 'product__category').prefetch_related(
            'product__images', 'product__tags'
        )
    
    def list(self, request, *args, **kwargs):
        """
        List all favorite products for the authenticated user
        
        GET /api/favorites/
        """
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response_data = self.get_paginated_response(serializer.data).data
            response_data['message'] = 'Sevimli mahsulotlar ro\'yxati'
            return Response(response_data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'message': 'Sevimli mahsulotlar ro\'yxati',
            'results': serializer.data,
            'count': queryset.count()
        })
    
    def create(self, request, *args, **kwargs):
        """
        Add a product to user's favorites
        
        POST /api/favorites/
        Body: { "product_id": "<uuid>" }
        """
        serializer = AddToFavoritesSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                favorite = serializer.save()
                
                # Log the action
                logger.info(
                    f"User {request.user.username} added product "
                    f"{favorite.product.name_uz} to favorites"
                )
                
                response_serializer = FavoriteSerializer(
                    favorite, 
                    context={'request': request}
                )
                
                return Response({
                    'message': 'Mahsulot sevimlilar ro\'yxatiga qo\'shildi',
                    'favorite': response_serializer.data
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            logger.error(f"Error adding to favorites: {str(e)}")
            return Response({
                'error': 'Xatolik yuz berdi'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, *args, **kwargs):
        """
        Remove a product from user's favorites
        
        DELETE /api/favorites/<id>/
        """
        try:
            favorite = self.get_object()
            product_name = favorite.product.name_uz
            
            favorite.delete()
            
            logger.info(
                f"User {request.user.username} removed product "
                f"{product_name} from favorites"
            )
            
            return Response({
                'message': 'Mahsulot sevimlilar ro\'yxatidan o\'chirildi'
            }, status=status.HTTP_200_OK)
            
        except Favorite.DoesNotExist:
            return Response({
                'error': 'Sevimli mahsulot topilmadi'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def check(self, request):
        """
        Check if a product is in user's favorites
        
        GET /api/favorites/check/?product_id=<uuid>
        """
        product_id = request.query_params.get('product_id')
        
        if not product_id:
            return Response({
                'error': 'product_id parametri majburiy'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Validate UUID format
            import uuid
            uuid.UUID(product_id)
        except ValueError:
            return Response({
                'error': 'Noto\'g\'ri product_id formati'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if product exists
        try:
            product = Product.objects.get(
                id=product_id, 
                is_active=True, 
                deleted_at__isnull=True
            )
        except Product.DoesNotExist:
            return Response({
                'error': 'Mahsulot topilmadi'
            }, status=status.HTTP_404_NOT_FOUND)
        
        is_favorite = Favorite.is_favorited_by_user(request.user, product)
        
        serializer = FavoriteCheckSerializer({
            'is_favorite': is_favorite,
            'product_id': product_id
        })
        
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def toggle(self, request):
        """
        Toggle favorite status for a product
        
        POST /api/favorites/toggle/
        Body: { "product_id": "<uuid>" }
        """
        product_id = request.data.get('product_id')
        
        if not product_id:
            return Response({
                'error': 'product_id majburiy'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            product = Product.objects.get(
                id=product_id,
                is_active=True,
                deleted_at__isnull=True
            )
        except Product.DoesNotExist:
            return Response({
                'error': 'Mahsulot topilmadi'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            with transaction.atomic():
                favorite, created = Favorite.toggle_favorite(request.user, product)
                
                if created:
                    # Product was added to favorites
                    response_serializer = FavoriteSerializer(
                        favorite,
                        context={'request': request}
                    )
                    return Response({
                        'message': 'Mahsulot sevimlilar ro\'yxatiga qo\'shildi',
                        'is_favorite': True,
                        'favorite': response_serializer.data
                    }, status=status.HTTP_201_CREATED)
                else:
                    # Product was removed from favorites
                    return Response({
                        'message': 'Mahsulot sevimlilar ro\'yxatidan o\'chirildi',
                        'is_favorite': False
                    }, status=status.HTTP_200_OK)
                    
        except Exception as e:
            logger.error(f"Error toggling favorite: {str(e)}")
            return Response({
                'error': 'Xatolik yuz berdi'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['delete'])
    def clear(self, request):
        """
        Clear all favorites for the user
        
        DELETE /api/favorites/clear/
        """
        try:
            count = self.get_queryset().count()
            self.get_queryset().delete()
            
            logger.info(
                f"User {request.user.username} cleared {count} favorites"
            )
            
            return Response({
                'message': f'{count} ta sevimli mahsulot o\'chirildi',
                'cleared_count': count
            })
            
        except Exception as e:
            logger.error(f"Error clearing favorites: {str(e)}")
            return Response({
                'error': 'Xatolik yuz berdi'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get favorites statistics for the user
        
        GET /api/favorites/stats/
        """
        try:
            favorites = self.get_queryset()
            
            # Calculate statistics
            total_favorites = favorites.count()
            
            if total_favorites == 0:
                stats_data = {
                    'total_favorites': 0,
                    'categories_count': 0,
                    'most_favorited_category': None,
                    'average_price': 0,
                    'on_sale_count': 0
                }
            else:
                # Get category statistics
                category_stats = favorites.values(
                    'product__category__name_uz'
                ).annotate(
                    count=Count('id')
                ).order_by('-count').first()
                
                most_favorited_category = (
                    category_stats['product__category__name_uz'] 
                    if category_stats else None
                )
                
                categories_count = favorites.values(
                    'product__category'
                ).distinct().count()
                
                # Price statistics
                price_stats = favorites.aggregate(
                    avg_price=Avg('product__price')
                )
                
                # On sale count
                on_sale_count = favorites.filter(
                    product__sale_price__isnull=False,
                    product__sale_price__lt=F('product__price')
                ).count()
                
                stats_data = {
                    'total_favorites': total_favorites,
                    'categories_count': categories_count,
                    'most_favorited_category': most_favorited_category,
                    'average_price': price_stats['avg_price'] or 0,
                    'on_sale_count': on_sale_count
                }
            
            serializer = FavoriteStatsSerializer(stats_data)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error getting favorites stats: {str(e)}")
            return Response({
                'error': 'Statistika olishda xatolik yuz berdi'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def favorites_info(request):
    """
    Get favorites API information
    """
    return Response({
        'title': 'Sevimli mahsulotlar API',
        'description': 'Foydalanuvchilar sevimli mahsulotlarini boshqarish uchun API',
        'endpoints': {
            'list_favorites': '/api/favorites/ (GET)',
            'add_favorite': '/api/favorites/ (POST)',
            'remove_favorite': '/api/favorites/<id>/ (DELETE)',
            'check_favorite': '/api/favorites/check/?product_id=<uuid> (GET)',
            'toggle_favorite': '/api/favorites/toggle/ (POST)',
            'clear_favorites': '/api/favorites/clear/ (DELETE)',
            'favorites_stats': '/api/favorites/stats/ (GET)',
        },
        'features': [
            'Mahsulotlarni sevimlilar ro\'yxatiga qo\'shish',
            'Sevimli mahsulotlarni ko\'rish (pagination bilan)',
            'Sevimli mahsulotlarni o\'chirish',
            'Mahsulot sevimli ekanligini tekshirish',
            'Sevimli holатни toggle qilish',
            'Barcha sevimlilarni tozalash',
            'Sevimlilar statistikasi'
        ],
        'authentication': 'JWT Bearer Token majburiy',
        'pagination': {
            'page_size': 20,
            'max_page_size': 100
        }
    })
