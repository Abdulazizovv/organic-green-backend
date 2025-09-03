"""
Favorites models for Organic Green e-commerce
"""
from django.db import models
from django.contrib.auth import get_user_model
from apps.products.models import Product

User = get_user_model()

class Favorite(models.Model):
    """
    User's favorite products (Wishlist)
    
    This model represents the many-to-many relationship between users and their favorite products.
    Ensures that each user can only favorite a product once.
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Foydalanuvchi'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name='Mahsulot'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Qo\'shilgan sana'
    )
    
    class Meta:
        verbose_name = 'Sevimli mahsulot'
        verbose_name_plural = 'Sevimli mahsulotlar'
        # Ensure uniqueness: one user cannot favorite the same product twice
        unique_together = ('user', 'product')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.user.username} - {self.product.name_uz}"
    
    @classmethod
    def is_favorited_by_user(cls, user, product):
        """
        Check if a product is favorited by a specific user
        
        Args:
            user: User instance
            product: Product instance
            
        Returns:
            bool: True if product is in user's favorites, False otherwise
        """
        if not user.is_authenticated:
            return False
        return cls.objects.filter(user=user, product=product).exists()
    
    @classmethod
    def toggle_favorite(cls, user, product):
        """
        Toggle favorite status for a product by user
        
        Args:
            user: User instance
            product: Product instance
            
        Returns:
            tuple: (favorite_instance_or_None, created_or_deleted_bool)
                  - (favorite, True) if favorite was created
                  - (None, False) if favorite was removed
        """
        favorite, created = cls.objects.get_or_create(
            user=user,
            product=product
        )
        
        if not created:
            # Favorite exists, remove it
            favorite.delete()
            return None, False
        
        return favorite, True
