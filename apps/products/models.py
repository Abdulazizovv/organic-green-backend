from django.db import models
from django.utils import timezone
import uuid
from django.utils.text import slugify
import os


def product_image_upload_path(instance, filename):
    """Generate upload path for product images"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('products', str(instance.product.id), filename)


class ProductCategory(models.Model):
    # Multilingual fields for category name
    name_uz = models.CharField(max_length=255)
    name_ru = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255)
    
    description_uz = models.TextField(null=True, blank=True)
    description_ru = models.TextField(null=True, blank=True)
    description_en = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name_uz
    
    class Meta:
        verbose_name = "Mahsulot Kategoriyasi"
        verbose_name_plural = "Mahsulot Kategoriyalari"
    
class ProductTag(models.Model):
    # Multilingual fields for tag name
    name_uz = models.CharField(max_length=100)
    name_ru = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name_uz
    
    class Meta:
        verbose_name = "Mahsulot Teg"
        verbose_name_plural = "Mahsulot Teglari"


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Multilingual fields for product name and description
    name_uz = models.CharField(max_length=255)
    name_ru = models.CharField(max_length=255)
    name_en = models.CharField(max_length=255)

    slug = models.SlugField(max_length=255, unique=True)

    description_uz = models.TextField(null=True, blank=True)
    description_ru = models.TextField(null=True, blank=True)
    description_en = models.TextField(null=True, blank=True)
    
    
    price = models.DecimalField(max_digits=15, decimal_places=2)
    sale_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    
    category: "ProductCategory" = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='products')
    tags: "ProductTag" = models.ManyToManyField(ProductTag, related_name='products', blank=True)
    
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    suggested_products: "Product" = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='suggested_for', help_text="Ushbu mahsulotga qiziqqan foydalanuvchilarga tavsiya qilinadigan mahsulotlar")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"
    
    def __str__(self):
        return self.name_uz
    
    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.save()
    
    def restore(self):
        self.deleted_at = None
        self.save()
        
    @property
    def is_on_sale(self):
        return self.sale_price is not None and self.sale_price < self.price
    
    @property
    def available_stock(self):
        return self.stock > 0 and self.is_active and self.deleted_at is None
    
    @property
    def display_name(self):
        return f"{self.name_uz} ({self.name_en})"
    
    @property
    def final_price(self):
        return self.sale_price if self.is_on_sale else self.price
    
    @property
    def primary_image(self):
        """Get the primary image for this product"""
        primary = self.images.filter(is_primary=True).first()
        if primary:
            return primary
        return self.images.first()
    
    @property
    def all_images(self):
        """Get all images for this product ordered by order field"""
        return self.images.all()
    
    @property
    def image_count(self):
        """Get total number of images for this product"""
        return self.images.count()
    
    @property
    def tag_list(self, language='uz'):
        if language == 'uz':
            return [tag.name_uz for tag in self.tags.all()]
        elif language == 'ru':
            return [tag.name_ru for tag in self.tags.all()]
        elif language == 'en':
            return [tag.name_en for tag in self.tags.all()]
        return []
    
    @property
    def category_name(self, language='uz'):
        if language == 'uz':
            return self.category.name_uz
        elif language == 'ru':
            return self.category.name_ru
        elif language == 'en':
            return self.category.name_en
        return ''
    
    def active_products(self):
        return Product.objects.filter(is_active=True, deleted_at__isnull=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_uz)
        super().save(*args, **kwargs)


class ProductImage(models.Model):
    """Model for storing multiple images for each product"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=product_image_upload_path)
    alt_text_uz = models.CharField(max_length=255, blank=True, help_text="Alt matn (O'zbek)")
    alt_text_ru = models.CharField(max_length=255, blank=True, help_text="Alt matn (Rus)")
    alt_text_en = models.CharField(max_length=255, blank=True, help_text="Alt text (English)")
    is_primary = models.BooleanField(default=False, help_text="Asosiy rasm")
    order = models.PositiveIntegerField(default=0, help_text="Rasmlarni tartib raqami")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = "Mahsulot rasmi"
        verbose_name_plural = "Mahsulot rasmlari"

    def __str__(self):
        return f"{self.product.name_uz} - Image {self.order}"

    def save(self, *args, **kwargs):
        # If this is marked as primary, unmark all other images for this product
        if self.is_primary:
            ProductImage.objects.filter(product=self.product, is_primary=True).exclude(id=self.id).update(is_primary=False)
        super().save(*args, **kwargs)