"""
Custom User model for Organic Green e-commerce
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model with additional profile fields
    """
    # Profile fields
    avatar = models.ImageField(
        upload_to='avatars/',
        default='avatars/default.png',  # Make sure to add default avatar file
        blank=True,
        null=True,
        help_text="User profile avatar"
    )
    phone = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        help_text="User phone number"
    )
    is_verified = models.BooleanField(
        default=False,
        help_text="Whether user has verified their account"
    )
    
    # Override first_name and last_name to have proper length
    first_name = models.CharField(
        max_length=150,
        blank=True,
        help_text="User's first name"
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        help_text="User's last name"
    )
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        db_table = 'auth_user'  # Keep same table name to avoid migration issues
    
    @property
    def full_name(self):
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        return self.username
    
    @property
    def display_name(self):
        """Get display name for UI"""
        full_name = self.full_name
        if full_name != self.username:
            return full_name
        return self.username
    
    def __str__(self):
        return self.username
