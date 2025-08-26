from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Q
from django.utils import timezone
from apps.products.models import Product, ProductCategory, ProductTag, ProductImage


class ProductImageInline(admin.TabularInline):
    """Product ichida rasmlarni boshqarish uchun inline admin"""
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text_uz', 'alt_text_ru', 'alt_text_en', 'is_primary', 'order', 'image_preview')
    readonly_fields = ('image_preview',)
    ordering = ('order',)
    
    def image_preview(self, obj):
        """Rasm preview ko'rsatish"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 100px;" />',
                obj.image.url
            )
        return "Rasm yo'q"
    image_preview.short_description = "Preview"


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """ProductImage modelini boshqarish uchun admin interface"""
    
    list_display = ('product', 'image_preview', 'alt_text_uz', 'is_primary', 'order', 'created_at')
    list_filter = ('is_primary', 'created_at', 'product__category')
    search_fields = ('product__name_uz', 'product__name_ru', 'product__name_en', 'alt_text_uz', 'alt_text_ru', 'alt_text_en')
    list_editable = ('is_primary', 'order')
    ordering = ('product', 'order', 'created_at')
    readonly_fields = ('id', 'image_preview', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': (
                'product',
                'image',
                'image_preview',
                ('is_primary', 'order'),
            )
        }),
        ('Alt matnlar', {
            'fields': (
                'alt_text_uz',
                'alt_text_ru', 
                'alt_text_en',
            )
        }),
        ('Vaqt ma\'lumotlari', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def image_preview(self, obj):
        """Rasm preview ko'rsatish"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 300px;" />',
                obj.image.url
            )
        return "Rasm yo'q"
    image_preview.short_description = "Rasm Preview"
    
    def get_queryset(self, request):
        """Optimized queryset"""
        return super().get_queryset(request).select_related('product')


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    """ProductCategory modelini boshqarish uchun admin interface"""
    
    list_display = ('name_uz', 'name_ru', 'name_en', 'products_count', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name_uz', 'name_ru', 'name_en', 'description_uz', 'description_ru', 'description_en')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': (
                ('name_uz', 'name_ru', 'name_en'),
            )
        }),
        ('Tavsiflar', {
            'fields': (
                'description_uz',
                'description_ru', 
                'description_en',
            ),
            'classes': ('collapse',)
        }),
        ('Vaqt ma\'lumotlari', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def products_count(self, obj):
        """Kategoriyadagi mahsulotlar soni"""
        count = obj.products.filter(deleted_at__isnull=True).count()
        if count > 0:
            url = reverse('admin:products_product_changelist') + '?category__id__exact={}'.format(obj.id)
            return format_html('<a href="{}">{} ta mahsulot</a>', url, count)
        return "0 ta mahsulot"
    products_count.short_description = "Mahsulotlar soni"
    
    def get_queryset(self, request):
        """Optimized queryset with product count"""
        return super().get_queryset(request).annotate(
            products_count=Count('products', filter=Q(products__deleted_at__isnull=True))
        )


@admin.register(ProductTag)
class ProductTagAdmin(admin.ModelAdmin):
    """ProductTag modelini boshqarish uchun admin interface"""
    
    list_display = ('name_uz', 'name_ru', 'name_en', 'products_count', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name_uz', 'name_ru', 'name_en')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Tag nomi', {
            'fields': (
                ('name_uz', 'name_ru', 'name_en'),
            )
        }),
        ('Vaqt ma\'lumotlari', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def products_count(self, obj):
        """Tag bilan bog'langan mahsulotlar soni"""
        count = obj.products.filter(deleted_at__isnull=True).count()
        if count > 0:
            url = reverse('admin:products_product_changelist') + '?tags__id__exact={}'.format(obj.id)
            return format_html('<a href="{}">{} ta mahsulot</a>', url, count)
        return "0 ta mahsulot"
    products_count.short_description = "Mahsulotlar soni"


class ProductTagInline(admin.TabularInline):
    """Mahsulot sahifasida taglarni inline ko'rsatish"""
    model = Product.tags.through
    extra = 1
    verbose_name = "Tag"
    verbose_name_plural = "Taglar"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Product modelini boshqarish uchun admin interface"""
    
    inlines = [ProductImageInline]
    
    list_display = (
        'name_uz', 
        'category', 
        'price_display', 
        'primary_image_preview',
        'images_count', 
        'sale_price_display',
        'stock',
        'stock_status',
        'status_display',
        'is_active',
        'is_featured',
        'created_at'
    )
    
    list_filter = (
        'is_active',
        'is_featured', 
        'category',
        'tags',
        'created_at',
        'updated_at',
        ('deleted_at', admin.BooleanFieldListFilter),
    )
    
    search_fields = (
        'name_uz', 'name_ru', 'name_en',
        'description_uz', 'description_ru', 'description_en',
        'category__name_uz', 'category__name_ru', 'category__name_en'
    )
    
    list_editable = ('stock', 'is_active', 'is_featured')
    
    ordering = ('-created_at',)
    
    readonly_fields = (
        'id', 'created_at', 'updated_at', 'deleted_at',
        'is_on_sale', 'available_stock', 'final_price'
    )
    
    prepopulated_fields = {'slug': ('name_uz',)}
    
    filter_horizontal = ('tags', 'suggested_products')
    
    date_hierarchy = 'created_at'
    
    list_per_page = 25
    
    actions = [
        'make_active', 'make_inactive', 'make_featured', 
        'remove_featured', 'restore_products', 'soft_delete_products'
    ]
    
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': (
                'id',
                ('name_uz', 'name_ru', 'name_en'),
                'slug',
                'category',
            )
        }),
        ('Tavsiflar', {
            'fields': (
                'description_uz',
                'description_ru',
                'description_en',
            ),
            'classes': ('collapse',)
        }),
        ('Narx va zaxira', {
            'fields': (
                ('price', 'sale_price', 'final_price'),
                ('stock', 'available_stock'),
            )
        }),
        ('Holat', {
            'fields': (
                ('is_active', 'is_featured'),
                ('is_on_sale',),
            )
        }),
        ('Bog\'lanishlar', {
            'fields': (
                'tags',
                'suggested_products',
            ),
            'classes': ('collapse',)
        }),
        ('Vaqt ma\'lumotlari', {
            'fields': ('created_at', 'updated_at', 'deleted_at'),
            'classes': ('collapse',)
        })
    )
    
    def price_display(self, obj):
        """Narxni formatlangan ko'rinishda ko'rsatish"""
        price_str = "{:,.2f}".format(float(obj.price))
        return price_str + " so'm"
    price_display.short_description = "Narxi"
    
    def primary_image_preview(self, obj):
        """Asosiy rasmni preview ko'rsatish"""
        primary_image = obj.primary_image
        if primary_image and primary_image.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                primary_image.image.url
            )
        return "Rasm yo'q"
    primary_image_preview.short_description = "Asosiy rasm"
    
    def images_count(self, obj):
        """Mahsulotdagi rasmlar sonini ko'rsatish"""
        count = obj.image_count
        if count > 0:
            return format_html(
                '<span style="color: green; font-weight: bold;">{} ta rasm</span>',
                count
            )
        return format_html('<span style="color: red;">Rasm yo\'q</span>')
    images_count.short_description = "Rasmlar soni"
    
    def sale_price_display(self, obj):
        """Chegirmali narxni ko'rsatish"""
        if obj.sale_price:
            discount_percent = ((obj.price - obj.sale_price) / obj.price) * 100
            price_str = "{:,.2f}".format(float(obj.sale_price))
            discount_str = "{}%".format(round(float(discount_percent), 1))
            return format_html(
                '<span style="color: red; font-weight: bold;">{} so\'m</span><br>'
                '<small style="color: green;">{} chegirma</small>',
                price_str, discount_str
            )
        return "-"
    sale_price_display.short_description = "Chegirmali narx"
    
    def stock_status(self, obj):
        """Zaxira holatini ko'rsatish"""
        if obj.stock == 0:
            return format_html('<span style="color: red; font-weight: bold;">Tugagan</span>')
        elif obj.stock <= 10:
            return format_html('<span style="color: orange; font-weight: bold;">{} ta (Kam qoldi)</span>', obj.stock)
        else:
            return format_html('<span style="color: green;">{} ta</span>', obj.stock)
    stock_status.short_description = "Zaxira holati"
    
    def status_display(self, obj):
        """Mahsulot holatini ko'rsatish"""
        if obj.deleted_at:
            return format_html('<span style="color: red;">❌ O\'chirilgan</span>')
        elif obj.is_active:
            return format_html('<span style="color: green;">✅ Faol</span>')
        else:
            return format_html('<span style="color: orange;">⏸️ Nofaol</span>')
    status_display.short_description = "Holat"
    
    def get_queryset(self, request):
        """O'chirilgan mahsulotlarni ham ko'rsatish"""
        return super().get_queryset(request).select_related('category').prefetch_related('tags')
    
    # Admin actions
    def make_active(self, request, queryset):
        """Tanlangan mahsulotlarni faol qilish"""
        updated = queryset.update(is_active=True)
        self.message_user(request, '{} ta mahsulot faol qilindi.'.format(updated))
    make_active.short_description = "Tanlangan mahsulotlarni faol qilish"
    
    def make_inactive(self, request, queryset):
        """Tanlangan mahsulotlarni nofaol qilish"""
        updated = queryset.update(is_active=False)
        self.message_user(request, '{} ta mahsulot nofaol qilindi.'.format(updated))
    make_inactive.short_description = "Tanlangan mahsulotlarni nofaol qilish"
    
    def make_featured(self, request, queryset):
        """Tanlangan mahsulotlarni tavsiya etilgan qilish"""
        updated = queryset.update(is_featured=True)
        self.message_user(request, '{} ta mahsulot tavsiya etilgan deb belgilandi.'.format(updated))
    make_featured.short_description = "Tavsiya etilgan deb belgilash"
    
    def remove_featured(self, request, queryset):
        """Tanlangan mahsulotlardan tavsiya etilgan holatni olib tashlash"""
        updated = queryset.update(is_featured=False)
        self.message_user(request, '{} ta mahsulotdan tavsiya etilgan holat olib tashlandi.'.format(updated))
    remove_featured.short_description = "Tavsiya etilgan holatni olib tashlash"
    
    def restore_products(self, request, queryset):
        """O'chirilgan mahsulotlarni tiklash"""
        restored = 0
        for product in queryset:
            if product.deleted_at:
                product.restore()
                restored += 1
        self.message_user(request, '{} ta mahsulot tiklandi.'.format(restored))
    restore_products.short_description = "O'chirilgan mahsulotlarni tiklash"
    
    def soft_delete_products(self, request, queryset):
        """Mahsulotlarni yumshoq o'chirish"""
        deleted = 0
        for product in queryset:
            if not product.deleted_at:
                product.delete()
                deleted += 1
        self.message_user(request, '{} ta mahsulot o\'chirildi.'.format(deleted))
    soft_delete_products.short_description = "Mahsulotlarni o'chirish (soft delete)"
    
    def save_model(self, request, obj, form, change):
        """Mahsulot saqlashda qo'shimcha tekshiruvlar"""
        # Slug avtomatik generatsiya qilish
        if not obj.slug:
            obj.slug = obj.name_uz
        
        super().save_model(request, obj, form, change)
    
    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        js = ('admin/js/custom_admin.js',)

