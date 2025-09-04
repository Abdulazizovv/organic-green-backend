"""
Franchise application models
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class FranchiseApplication(models.Model):
    """
    Model for franchise application submissions
    """
    STATUS_CHOICES = [
        ('pending', 'Yangi'),
        ('reviewed', 'Ko\'rib chiqilgan'),
        ('approved', 'Ma\'qullangan'),
        ('rejected', 'Rad etilgan'),
    ]

    # Required fields
    full_name = models.CharField(
        max_length=255,
        help_text="Ariza beruvchining to'liq ismi"
    )
    phone = models.CharField(
        max_length=20,
        help_text="Ariza beruvchining telefon raqami"
    )
    city = models.CharField(
        max_length=100,
        help_text="Franshiza joylashadigan shahar"
    )
    investment_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Mavjud investitsiya miqdori AQSh dollarida"
    )
    
    # Optional fields
    email = models.EmailField(
        blank=True,
        null=True,
        help_text="Ariza beruvchining elektron pochta manzili"
    )
    experience = models.TextField(
        blank=True,
        null=True,
        help_text="Oldingi biznes tajribasi yoki franshiza tajribasi"
    )
    message = models.TextField(
        blank=True,
        null=True,
        help_text="Qo'shimcha xabar yoki izohlar"
    )
    
    # Status and metadata
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Ariza holati"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Ariza berilgan vaqt"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Ariza oxirgi marta yangilangan vaqt"
    )

    class Meta:
        verbose_name = 'Franshiza arizasi'
        verbose_name_plural = 'Franshiza arizalari'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.city} ({self.status})"

    @property
    def is_pending(self):
        """Check if application is pending"""
        return self.status == 'pending'

    @property
    def is_approved(self):
        """Check if application is approved"""
        return self.status == 'approved'

    @property
    def formatted_investment_amount(self):
        """Get formatted investment amount"""
        return f"${self.investment_amount:,.2f}"
