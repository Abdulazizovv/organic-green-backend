"""
Order models for Organic Green e-commerce
"""
import uuid
from decimal import Decimal
from django.db import models, transaction
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator
from apps.products.models import Product

User = get_user_model()

class OrderStatus(models.TextChoices):
    """Order status choices"""
    PENDING = 'pending', 'Kutilmoqda'
    PAID = 'paid', "To'langan"
    PROCESSING = 'processing', 'Qayta ishlanmoqda'
    SHIPPED = 'shipped', "Jo'natildi"
    DELIVERED = 'delivered', 'Yetkazildi'
    CANCELED = 'canceled', 'Bekor qilindi'


class PaymentMethod(models.TextChoices):
    """Payment method choices"""
    COD = 'cod', 'Naqd / Kuryerga'
    CLICK = 'click', 'Click'
    PAYME = 'payme', 'Payme'
    CARD = 'card', 'Bank karta'
    NONE = 'none', "To'lovsiz"


class Order(models.Model):
    """
    Order model for storing customer orders
    Supports both authenticated and anonymous users
    """
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    order_number = models.CharField(
        max_length=32, 
        unique=True, 
        editable=False,
        db_index=True,
        help_text="Unique order number in format OG-YYYYMMDD-00001"
    )
    
    # User identification (authenticated or anonymous)
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='orders',
        help_text="Order owner (null for anonymous orders)"
    )
    session_key = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
        help_text="Session key for anonymous orders"
    )
    
    # Order status and payment
    status = models.CharField(
        max_length=16,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
        db_index=True
    )
    payment_method = models.CharField(
        max_length=16,
        choices=PaymentMethod.choices,
        default=PaymentMethod.COD
    )
    
    # Contact information (snapshot)
    full_name = models.CharField(
        max_length=150,
        help_text="Customer full name",
        null=True,
        blank=True
    )
    contact_phone = models.CharField(
        max_length=32,
        help_text="Customer phone number",
        null=True,
        blank=True
    )
    delivery_address = models.TextField(
        help_text="Delivery address",
        null=True,
        blank=True
    )
    notes = models.TextField(
        blank=True,
        help_text="Special instructions or notes"
    )
    
    # Financial totals
    
    delivery_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Delivery fee"
    )
    
    subtotal = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Subtotal before discounts"
    )
    discount_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Total discount amount"
    )
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Final total price"
    )
    total_items = models.PositiveIntegerField(
        default=0,
        help_text="Total quantity of items"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Buyurtma'
        verbose_name_plural = 'Buyurtmalar'
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['session_key', 'created_at']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.order_number} ({self.get_status_display()})"
    
    def generate_order_number(self):
        """Generate unique order number for current day"""
        today = timezone.now().date()
        date_part = today.strftime('%Y%m%d')
        
        # Get count of orders created today (with select_for_update for race condition safety)
        with transaction.atomic():
            today_orders_count = Order.objects.select_for_update().filter(
                created_at__date=today
            ).count()
            
            sequence = today_orders_count + 1
            return f"OG-{date_part}-{sequence:05d}"
    
    def save(self, *args, **kwargs):
        """Override save to generate order number"""
        if not self.order_number:
            self.order_number = self.generate_order_number()
        
        # Calculate total_price
        self.total_price = self.subtotal - self.discount_total
        
        super().save(*args, **kwargs)
    
    @property
    def is_cancellable(self):
        """Check if order can be cancelled"""
        return self.status in [OrderStatus.PENDING, OrderStatus.PROCESSING]
    
    @property
    def customer_display(self):
        """Get customer display name"""
        if self.user:
            return f"{self.user.username} ({self.full_name})"
        return f"Guest ({self.full_name})"


class OrderItem(models.Model):
    """
    Order item model - snapshot of cart items at time of order
    """
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE
    )
    
    # Product reference (nullable for deleted products)
    product = models.ForeignKey(
        Product,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text="Original product reference",
        related_name='order_items'
    )
    
    # Product snapshot data
    product_name = models.CharField(
        max_length=255,
        help_text="Product name at time of order"
    )
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Quantity ordered"
    )
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Price per unit at time of order"
    )
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Total price for this item (quantity * unit_price)"
    )
    is_sale_price = models.BooleanField(
        default=False,
        help_text="Whether sale price was applied"
    )
    
    class Meta:
        verbose_name = 'Buyurtma elementi'
        verbose_name_plural = 'Buyurtma elementlari'
        indexes = [
            models.Index(fields=['order', 'product']),
        ]
    
    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        """Override save to calculate total_price"""
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
