from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from apps.products.models import Product
import uuid

User = get_user_model()

class Cart(models.Model):
    """
    Shopping Cart Model
    Represents a user's shopping cart
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='cart',
        null=True, 
        blank=True,
        help_text="Cart owner (null for anonymous users)"
    )
    session_key = models.CharField(
        max_length=255, 
        null=True, 
        blank=True,
        help_text="Session key for anonymous users"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Savat"
        verbose_name_plural = "Savatlar"
        ordering = ['-updated_at']
        
    def __str__(self):
        if self.user:
            return f"Savat - {self.user.username}"
        return f"Anonim savat - {self.session_key[:8]}..."
    
    @property
    def total_items(self):
        """Total number of items in cart"""
        return sum(item.quantity for item in self.items.all())
    
    @property
    def total_price(self):
        """Total price of all items in cart"""
        return sum(item.get_total_price() for item in self.items.all())
    
    @property
    def items_count(self):
        """Number of different products in cart"""
        return self.items.count()
    
    def clear(self):
        """Remove all items from cart"""
        self.items.all().delete()
        
    def is_empty(self):
        """Check if cart is empty"""
        return not self.items.exists()


class CartItem(models.Model):
    """
    Cart Item Model
    Represents individual items in a shopping cart
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(
        Cart, 
        on_delete=models.CASCADE, 
        related_name='items'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[
            MinValueValidator(1, message="Miqdor kamida 1 bo'lishi kerak"),
            MaxValueValidator(999, message="Miqdor 999 dan oshmasligi kerak")
        ]
    )
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Savat elementi"
        verbose_name_plural = "Savat elementlari"
        unique_together = ('cart', 'product')  # One product per cart
        ordering = ['-updated_at']
        
    def __str__(self):
        return f"{self.product.name_uz} x {self.quantity}"
    
    def get_total_price(self):
        """Calculate total price for this cart item"""
        price = self.product.sale_price if self.product.sale_price else self.product.price
        return price * self.quantity
    
    def get_unit_price(self):
        """Get unit price (considering sale price)"""
        return self.product.sale_price if self.product.sale_price else self.product.price
    
    def save(self, *args, **kwargs):
        """Custom save method with validation"""
        # Note: Stock validation is now handled in the API layer
        # to provide better error responses to frontend
        
        # Update cart's updated_at when item is saved
        super().save(*args, **kwargs)
        self.cart.updated_at = timezone.now()
        self.cart.save(update_fields=['updated_at'])


class CartHistory(models.Model):
    """
    Cart History Model
    Tracks cart actions for analytics
    """
    ACTION_CHOICES = [
        ('add', 'Qo\'shildi'),
        ('update', 'Yangilandi'),
        ('remove', 'O\'chirildi'),
        ('clear', 'Tozalandi'),
        ('checkout', 'Xarid qilindi'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(
        Cart, 
        on_delete=models.CASCADE, 
        related_name='history'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    quantity = models.PositiveIntegerField(null=True, blank=True)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Savat tarixi"
        verbose_name_plural = "Savat tarixlari"
        ordering = ['-timestamp']
        
    def __str__(self):
        if self.product:
            return f"{self.get_action_display()} - {self.product.name_uz}"
        return f"{self.get_action_display()}"
