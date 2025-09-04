"""
Serializers for API
Professional-grade serializers with validation and optimization
"""
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from apps.products.models import Product, ProductCategory, ProductTag, ProductImage
from django.db.models import Avg, Count
import re


User = get_user_model()


# Authentication Serializers

class SimpleUserRegistrationSerializer(serializers.ModelSerializer):
    """Simple user registration - only username and password required"""
    
    password = serializers.CharField(
        write_only=True,
        min_length=4,
        help_text="Parol kamida 4 ta belgidan iborat bo'lishi kerak"
    )
    
    class Meta:
        model = User
        fields = ['id', 'username', 'password']
        read_only_fields = ['id']
        
    def validate_username(self, value):
        """Validate username"""
        if len(value) < 3:
            raise serializers.ValidationError(
                "Foydalanuvchi nomi kamida 3 ta belgidan iborat bo'lishi kerak."
            )
            
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "Bu foydalanuvchi nomi allaqachon band."
            )
            
        return value
        
    def validate_password(self, value):
        """Simple password validation"""
        if len(value) < 4:
            raise serializers.ValidationError(
                "Parol kamida 4 ta belgidan iborat bo'lishi kerak."
            )
        return value
        
    def create(self, validated_data):
        """Create new user"""
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=f"{validated_data['username']}@temp.com"  # Temporary email
        )
        return user


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration - simplified version"""
    
    password = serializers.CharField(
        write_only=True,
        min_length=6,
        help_text="Password must be at least 6 characters long"
    )
    password_confirm = serializers.CharField(
        write_only=True,
        help_text="Confirm your password"
    )
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=False, max_length=30, allow_blank=True)
    last_name = serializers.CharField(required=False, max_length=30, allow_blank=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'password', 'password_confirm'
        ]
        read_only_fields = ['id']
        
    def validate_username(self, value):
        """Validate username"""
        if len(value) < 3:
            raise serializers.ValidationError(
                "Foydalanuvchi nomi kamida 3 ta belgidan iborat bo'lishi kerak."
            )
        
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError(
                "Foydalanuvchi nomida faqat harflar, raqamlar va pastki chiziq bo'lishi mumkin."
            )
            
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "Bu foydalanuvchi nomi allaqachon band."
            )
            
        return value
        
    def validate_email(self, value):
        """Validate email"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Bu email allaqon ro'yxatdan o'tgan."
            )
        return value
        
    def validate_password(self, value):
        """Validate password - simplified"""
        if len(value) < 6:
            raise serializers.ValidationError(
                "Parol kamida 6 ta belgidan iborat bo'lishi kerak."
            )
        return value
        
    def validate(self, attrs):
        """Validate password confirmation"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Parollar mos kelmaydi.'
            })
        return attrs
        
    def create(self, validated_data):
        """Create new user"""
        validated_data.pop('password_confirm')
        
        # Set default values for optional fields
        if not validated_data.get('first_name'):
            validated_data['first_name'] = ''
        if not validated_data.get('last_name'):
            validated_data['last_name'] = ''
            
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    
    username = serializers.CharField(
        required=True,
        help_text="Foydalanuvchi nomi yoki email"
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        help_text="Parol"
    )
    
    def validate(self, attrs):
        """Validate login credentials"""
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            # Try to authenticate with username first
            user = authenticate(username=username, password=password)
            
            # If that fails, try with email
            if not user:
                try:
                    user_obj = User.objects.get(email=username)
                    user = authenticate(username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass
            
            if not user:
                raise serializers.ValidationError(
                    'Foydalanuvchi nomi yoki parol noto\'g\'ri.'
                )
                
            if not user.is_active:
                raise serializers.ValidationError(
                    'Foydalanuvchi hisobi faol emas.'
                )
                
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError(
                'Foydalanuvchi nomi va parol kiritish majburiy.'
            )


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile with custom User model fields"""
    
    full_name = serializers.CharField(read_only=True)
    display_name = serializers.CharField(read_only=True)
    date_joined = serializers.DateTimeField(read_only=True)
    last_login = serializers.DateTimeField(read_only=True)
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'display_name', 'phone', 'avatar', 'avatar_url',
            'is_verified', 'is_active', 'is_staff', 'date_joined', 'last_login'
        ]
        read_only_fields = [
            'id', 'username', 'is_active', 'is_staff', 'date_joined', 'last_login',
            'full_name', 'display_name', 'avatar_url'
        ]
        
    def get_avatar_url(self, obj):
        """Get full URL for avatar image"""
        if obj.avatar and hasattr(obj.avatar, 'url'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None
        
    def validate_email(self, value):
        """Validate email during update"""
        user = self.instance
        if user and User.objects.filter(email=value).exclude(id=user.id).exists():
            raise serializers.ValidationError(
                "Bu email allaqon ro'yxatdan o'tgan."
            )
        return value
        
    def validate_phone(self, value):
        """Validate phone number"""
        if value and not value.startswith('+'):
            raise serializers.ValidationError(
                "Telefon raqam '+' belgisi bilan boshlanishi kerak."
            )
        if value and len(value) < 10:
            raise serializers.ValidationError(
                "Telefon raqam kamida 10 ta belgidan iborat bo'lishi kerak."
            )
        return value


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Enhanced user registration serializer with custom User model fields"""
    
    password = serializers.CharField(
        write_only=True,
        min_length=6,
        help_text="Parol kamida 6 ta belgidan iborat bo'lishi kerak"
    )
    password_confirm = serializers.CharField(
        write_only=True,
        help_text="Parolni tasdiqlang"
    )
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=False, max_length=150, allow_blank=True)
    last_name = serializers.CharField(required=False, max_length=150, allow_blank=True)
    phone = serializers.CharField(required=False, max_length=30, allow_blank=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone', 'password', 'password_confirm'
        ]
        read_only_fields = ['id']
        
    def validate_username(self, value):
        """Validate username"""
        if len(value) < 3:
            raise serializers.ValidationError(
                "Foydalanuvchi nomi kamida 3 ta belgidan iborat bo'lishi kerak."
            )
        
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError(
                "Foydalanuvchi nomida faqat harflar, raqamlar va pastki chiziq bo'lishi mumkin."
            )
            
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "Bu foydalanuvchi nomi allaqachon band."
            )
            
        return value
        
    def validate_email(self, value):
        """Validate email"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Bu email allaqon ro'yxatdan o'tgan."
            )
        return value
        
    def validate_phone(self, value):
        """Validate phone number"""
        if value and not value.startswith('+'):
            raise serializers.ValidationError(
                "Telefon raqam '+' belgisi bilan boshlanishi kerak."
            )
        if value and len(value) < 10:
            raise serializers.ValidationError(
                "Telefon raqam kamida 10 ta belgidan iborat bo'lishi kerak."
            )
        return value
        
    def validate_password(self, value):
        """Validate password"""
        if len(value) < 6:
            raise serializers.ValidationError(
                "Parol kamida 6 ta belgidan iborat bo'lishi kerak."
            )
        return value
        
    def validate(self, attrs):
        """Validate password confirmation"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Parollar mos kelmaydi.'
            })
        return attrs
        
    def create(self, validated_data):
        """Create new user with custom fields"""
        validated_data.pop('password_confirm')
        
        # Set default values for optional fields
        if not validated_data.get('first_name'):
            validated_data['first_name'] = ''
        if not validated_data.get('last_name'):
            validated_data['last_name'] = ''
        if not validated_data.get('phone'):
            validated_data['phone'] = ''
            
        user = User.objects.create_user(**validated_data)
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password"""
    
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, min_length=6)
    new_password_confirm = serializers.CharField(required=True, write_only=True)
    
    def validate_old_password(self, value):
        """Validate old password"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Eski parol noto\'g\'ri.')
        return value
        
    def validate_new_password(self, value):
        """Validate new password"""
        if len(value) < 6:
            raise serializers.ValidationError(
                "Yangi parol kamida 6 ta belgidan iborat bo'lishi kerak."
            )
        return value
        
    def validate(self, attrs):
        """Validate password confirmation"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Yangi parollar mos kelmaydi.'
            })
        return attrs
        
    def save(self):
        """Save new password"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer with additional user info"""
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        token['full_name'] = user.full_name
        token['phone'] = user.phone or ''
        token['is_verified'] = user.is_verified
        token['is_staff'] = user.is_staff
        
        return token
        
    def validate(self, attrs):
        """Allow login with email or username"""
        username = attrs.get('username')
        password = attrs.get('password')
        
        # Try to get user by email if username is email format
        if '@' in username:
            try:
                user = User.objects.get(email=username)
                attrs['username'] = user.username
            except User.DoesNotExist:
                pass
                
        data = super().validate(attrs)
        
        # Add user data to response
        data['user'] = UserProfileSerializer(self.user, context={'request': self.context.get('request')}).data
        
        return data


class AvatarUploadSerializer(serializers.ModelSerializer):
    """Serializer for avatar upload"""
    
    class Meta:
        model = User
        fields = ['avatar']
        
    def validate_avatar(self, value):
        """Validate avatar file"""
        if value:
            # Check file size (max 5MB)
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError(
                    "Rasm hajmi 5MB dan oshmasligi kerak."
                )
            
            # Check file type
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if value.content_type not in allowed_types:
                raise serializers.ValidationError(
                    "Faqat JPEG, PNG, GIF, WEBP formatidagi rasmlar qabul qilinadi."
                )
        
        return value


# Product Serializers


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
