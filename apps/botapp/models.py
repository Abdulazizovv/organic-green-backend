from django.db import models


class BotUser(models.Model):
    user_id = models.CharField(max_length=32, unique=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=32, null=True, blank=True)
    language_code = models.CharField(max_length=8, null=True, blank=True, default='uz')
    is_active = models.BooleanField(default=True)
    is_blocked = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Bot Foydalanuvchi"
        verbose_name_plural = "Bot Foydalanuvchilar"
        ordering = ['-created_at']