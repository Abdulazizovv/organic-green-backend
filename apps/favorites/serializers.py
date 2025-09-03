"""
Serializers for Favorites API
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from apps.products.models import Product
from .models import Favorite


class FavoriteProductSerializer(serializers.ModelSerializer):
    """
    Nested serializer for product details in favorites
    """
    final_price = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name_uz', read_only=True)
    is_on_sale = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name_uz', 'name_ru', 'name_en', 'slug',
            'price', 'sale_price', 'final_price', 'stock',
            'is_active', 'is_featured', 'image', 'category_name',
            'is_on_sale', 'created_at'
        ]
    
    def get_final_price(self, obj):
        """Get the final price (sale price if available, otherwise regular price)"""
        return obj.sale_price if obj.sale_price else obj.price
    
    def get_image(self, obj):
        """Get the first product image URL"""
        if obj.images.exists():
            request = self.context.get('request')
            image_url = obj.images.first().image.url
            if request:
                return request.build_absolute_uri(image_url)
            return image_url
        return None
    
    def get_is_on_sale(self, obj):
        """Check if product is on sale"""
        return bool(obj.sale_price and obj.sale_price < obj.price)


class FavoriteSerializer(serializers.ModelSerializer):
    """
    Serializer for Favorite model with nested product details
    """
    product = FavoriteProductSerializer(read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Favorite
        fields = ['id', 'user', 'product', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class AddToFavoritesSerializer(serializers.Serializer):
    """
    Serializer for adding products to favorites
    """
    product_id = serializers.UUIDField(
        help_text="UUID of the product to add to favorites"
    )
    
    def validate_product_id(self, value):
        """
        Validate that the product exists and is active
        """
        try:
            product = Product.objects.get(
                id=value, 
                is_active=True, 
                deleted_at__isnull=True
            )
        except Product.DoesNotExist:
            raise serializers.ValidationError(
                "Mahsulot topilmadi yoki faol emas."
            )
        return value
    
    def validate(self, data):
        """
        Check if product is already in user's favorites
        """
        user = self.context['request'].user
        product_id = data['product_id']
        
        if Favorite.objects.filter(user=user, product_id=product_id).exists():
            raise serializers.ValidationError({
                'product_id': 'Bu mahsulot allaqachon sevimlilar ro\'yxatida.'
            })
        
        return data
    
    def create(self, validated_data):
        """
        Create a new favorite
        """
        user = self.context['request'].user
        product = Product.objects.get(id=validated_data['product_id'])
        
        favorite = Favorite.objects.create(
            user=user,
            product=product
        )
        return favorite


class FavoriteCheckSerializer(serializers.Serializer):
    """
    Serializer for checking if a product is in favorites
    """
    is_favorite = serializers.BooleanField(read_only=True)
    product_id = serializers.UUIDField(read_only=True)


class FavoriteStatsSerializer(serializers.Serializer):
    """
    Serializer for favorite statistics
    """
    total_favorites = serializers.IntegerField(read_only=True)
    categories_count = serializers.IntegerField(read_only=True)
    most_favorited_category = serializers.CharField(read_only=True, allow_null=True)
    average_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    on_sale_count = serializers.IntegerField(read_only=True)
