from django.db import models
import uuid
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction



class Application(models.Model):
    """
    Model to store course applications submitted by users
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application_number = models.CharField(max_length=32, unique=True, help_text="Unikal ariza raqami")
    full_name = models.CharField(max_length=255, help_text="Ariza beruvchining to'liq ismi")
    email = models.EmailField(help_text="Ariza beruvchining email manzili")
    phone_number = models.CharField(max_length=20, help_text="Ariza beruvchining telefon raqami")
    course_name = models.CharField(max_length=255, help_text="Ariza berilgan kurs nomi")
    message = models.TextField(blank=True, help_text="Ariza beruvchidan qo'shimcha xabar")
    created_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False, help_text="Ariza qayta ishlanganmi")
    
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Kursga ariza"
        verbose_name_plural = "Kursga arizalar"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.course_name}"

    def generate_application_number(self):
        """Generate unique application number for current day"""
        today = timezone.now().date()
        date_part = today.strftime('%Y%m%d')

        # Get count of applications created today (with select_for_update for race condition safety)
        with transaction.atomic():
            today_applications_count = Application.objects.select_for_update().filter(
                created_at__date=today
            ).count()

            sequence = today_applications_count + 1
            return f"KURS-{date_part}-{sequence:05d}"

    def save(self, *args, **kwargs):
        """Override save to generate application number"""
        if not self.application_number:
            self.application_number = self.generate_application_number()

        super().save(*args, **kwargs)