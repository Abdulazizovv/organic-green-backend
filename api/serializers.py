"""
Serializers for Product API
Professional-grade serializers with validation and optimization
"""
from rest_framework import serializers
from apps.products.models import Product, ProductCategory, ProductTag, ProductImage
from django.db.models import Avg, Count


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for ProductImage model"""
    
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductImage
        fields = [
            'id', 'image', 'image_url',
            'alt_text_uz', 'alt_text_ru', 'alt_text_en',
            'is_primary', 'order',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'image_url']
    
    def get_image_url(self, obj):
        """Get full URL for the image"""
        if obj.image and hasattr(obj.image, 'url'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class ProductCategorySerializer(serializers.ModelSerializer):
    """Serializer for ProductCategory model"""
    
    products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductCategory
        fields = [
            'id',
            'name_uz', 'name_ru', 'name_en',
            'description_uz', 'description_ru', 'description_en',
            'products_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'products_count']
    
    def get_products_count(self, obj):
        """Get active products count for this category"""
        return obj.products.filter(is_active=True, deleted_at__isnull=True).count()


class ProductTagSerializer(serializers.ModelSerializer):
    """Serializer for ProductTag model"""
    
    products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductTag
        fields = [
            'id',
            'name_uz', 'name_ru', 'name_en',
            'products_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'products_count']
    
    def get_products_count(self, obj):
        """Get active products count for this tag"""
        return obj.products.filter(is_active=True, deleted_at__isnull=True).count()


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for product list views"""
    
    category = serializers.StringRelatedField()
    tags = ProductTagSerializer(many=True, read_only=True)
    final_price = serializers.ReadOnlyField()
    is_on_sale = serializers.ReadOnlyField()
    available_stock = serializers.ReadOnlyField()
    category_name = serializers.SerializerMethodField()
    primary_image = serializers.SerializerMethodField()
    images_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'slug',
            'name_uz', 'name_ru', 'name_en',
            'category', 'category_name',
            'price', 'sale_price', 'final_price',
            'is_on_sale', 'stock', 'available_stock',
            'tags', 'is_featured',
            'primary_image', 'images_count',
            'created_at'
        ]
    
    def get_category_name(self, obj):
        """Get localized category name"""
        language = self.context.get('language', 'uz')
        if language == 'uz':
            return obj.category.name_uz
        elif language == 'ru':
            return obj.category.name_ru
        elif language == 'en':
            return obj.category.name_en
        return obj.category.name_uz
    
    def get_primary_image(self, obj):
        """Get primary image for the product"""
        primary_image = obj.primary_image
        if primary_image:
            return ProductImageSerializer(primary_image, context=self.context).data
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single product views"""
    
    category = ProductCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductCategory.objects.all(),
        source='category',
        write_only=True
    )
    tags = ProductTagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=ProductTag.objects.all(),
        many=True,
        source='tags',
        write_only=True
    )
    suggested_products = ProductListSerializer(many=True, read_only=True)
    suggested_product_ids = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        many=True,
        source='suggested_products',
        write_only=True,
        required=False
    )
    
    # Image fields
    images = ProductImageSerializer(many=True, read_only=True)
    primary_image = serializers.SerializerMethodField()
    images_count = serializers.ReadOnlyField()
    
    # Computed fields
    final_price = serializers.ReadOnlyField()
    is_on_sale = serializers.ReadOnlyField()
    available_stock = serializers.ReadOnlyField()
    display_name = serializers.ReadOnlyField()
    
    # Localized fields
    localized_name = serializers.SerializerMethodField()
    localized_description = serializers.SerializerMethodField()
    localized_category_name = serializers.SerializerMethodField()
    localized_tags = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'slug',
            'name_uz', 'name_ru', 'name_en',
            'localized_name',
            'description_uz', 'description_ru', 'description_en',
            'localized_description',
            'category', 'category_id', 'localized_category_name',
            'tags', 'tag_ids', 'localized_tags',
            'price', 'sale_price', 'final_price', 'is_on_sale',
            'stock', 'available_stock',
            'is_active', 'is_featured',
            'suggested_products', 'suggested_product_ids',
            'images', 'primary_image', 'images_count',
            'display_name',
            'created_at', 'updated_at', 'deleted_at'
        ]
        read_only_fields = [
            'id', 'slug', 'final_price', 'is_on_sale', 'available_stock',
            'display_name', 'images_count', 'created_at', 'updated_at', 'deleted_at'
        ]
    
    def get_primary_image(self, obj):
        """Get primary image for the product"""
        primary_image = obj.primary_image
        if primary_image:
            return ProductImageSerializer(primary_image, context=self.context).data
        return None
    
    def get_localized_name(self, obj):
        """Get localized product name"""
        language = self.context.get('language', 'uz')
        if language == 'uz':
            return obj.name_uz
        elif language == 'ru':
            return obj.name_ru
        elif language == 'en':
            return obj.name_en
        return obj.name_uz
    
    def get_localized_description(self, obj):
        """Get localized product description"""
        language = self.context.get('language', 'uz')
        if language == 'uz':
            return obj.description_uz
        elif language == 'ru':
            return obj.description_ru
        elif language == 'en':
            return obj.description_en
        return obj.description_uz
    
    def get_localized_category_name(self, obj):
        """Get localized category name"""
        language = self.context.get('language', 'uz')
        if language == 'uz':
            return obj.category.name_uz
        elif language == 'ru':
            return obj.category.name_ru
        elif language == 'en':
            return obj.category.name_en
        return obj.category.name_uz
    
    def get_localized_tags(self, obj):
        """Get localized tag names"""
        language = self.context.get('language', 'uz')
        tags = []
        for tag in obj.tags.all():
            if language == 'uz':
                tags.append(tag.name_uz)
            elif language == 'ru':
                tags.append(tag.name_ru)
            elif language == 'en':
                tags.append(tag.name_en)
            else:
                tags.append(tag.name_uz)
        return tags
    
    def validate_price(self, value):
        """Validate product price"""
        if value <= 0:
            raise serializers.ValidationError("Narx 0 dan katta bo'lishi kerak.")
        return value
    
    def validate_sale_price(self, value):
        """Validate sale price"""
        if value is not None and value <= 0:
            raise serializers.ValidationError("Chegirmali narx 0 dan katta bo'lishi kerak.")
        return value
    
    def validate_stock(self, value):
        """Validate stock"""
        if value < 0:
            raise serializers.ValidationError("Zaxira soni manfiy bo'lishi mumkin emas.")
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        price = data.get('price')
        sale_price = data.get('sale_price')
        
        if sale_price and price and sale_price >= price:
            raise serializers.ValidationError({
                'sale_price': 'Chegirmali narx asosiy narxdan kichik bo\'lishi kerak.'
            })
        
        return data


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating products"""
    
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductCategory.objects.all(),
        source='category'
    )
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=ProductTag.objects.all(),
        many=True,
        source='tags',
        required=False
    )
    suggested_product_ids = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        many=True,
        source='suggested_products',
        required=False
    )
    
    class Meta:
        model = Product
        fields = [
            'name_uz', 'name_ru', 'name_en',
            'description_uz', 'description_ru', 'description_en',
            'category_id', 'tag_ids',
            'price', 'sale_price', 'stock',
            'is_active', 'is_featured',
            'suggested_product_ids'
        ]
    
    def validate_price(self, value):
        """Validate product price"""
        if value <= 0:
            raise serializers.ValidationError("Narx 0 dan katta bo'lishi kerak.")
        return value
    
    def validate_sale_price(self, value):
        """Validate sale price"""
        if value is not None and value <= 0:
            raise serializers.ValidationError("Chegirmali narx 0 dan katta bo'lishi kerak.")
        return value
    
    def validate_stock(self, value):
        """Validate stock"""
        if value < 0:
            raise serializers.ValidationError("Zaxira soni manfiy bo'lishi mumkin emas.")
        return value
    
    def validate(self, data):
        """Cross-field validation"""
        price = data.get('price')
        sale_price = data.get('sale_price')
        
        if sale_price and price and sale_price >= price:
            raise serializers.ValidationError({
                'sale_price': 'Chegirmali narx asosiy narxdan kichik bo\'lishi kerak.'
            })
        
        return data
    
    def create(self, validated_data):
        """Create product with proper slug generation"""
        tags = validated_data.pop('tags', [])
        suggested_products = validated_data.pop('suggested_products', [])
        
        product = Product.objects.create(**validated_data)
        
        if tags:
            product.tags.set(tags)
        if suggested_products:
            product.suggested_products.set(suggested_products)
        
        return product
    
    def update(self, instance, validated_data):
        """Update product"""
        tags = validated_data.pop('tags', None)
        suggested_products = validated_data.pop('suggested_products', None)
        
        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update many-to-many relationships
        if tags is not None:
            instance.tags.set(tags)
        if suggested_products is not None:
            instance.suggested_products.set(suggested_products)
        
        return instance


class ProductStatsSerializer(serializers.Serializer):
    """Serializer for product statistics"""
    
    total_products = serializers.IntegerField()
    active_products = serializers.IntegerField()
    featured_products = serializers.IntegerField()
    out_of_stock = serializers.IntegerField()
    low_stock = serializers.IntegerField()
    on_sale = serializers.IntegerField()
    categories_count = serializers.IntegerField()
    tags_count = serializers.IntegerField()
    average_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_stock_value = serializers.DecimalField(max_digits=15, decimal_places=2)
