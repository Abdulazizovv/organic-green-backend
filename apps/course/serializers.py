"""
Course Application Serializers
"""
from rest_framework import serializers
from django.core.validators import RegexValidator
from .models import Application


class ApplicationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating course applications (Public API)
    """
    phone_number = serializers.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?[1-9]\d{1,14}$',
                message="Telefon raqami to'g'ri formatda bo'lishi kerak. Masalan: +998901234567"
            )
        ],
        help_text="Telefon raqami +998901234567 formatida"
    )
    
    email = serializers.EmailField(
        help_text="Email manzili example@email.com formatida"
    )
    
    full_name = serializers.CharField(
        max_length=255,
        min_length=2,
        help_text="To'liq ism va familiya"
    )
    
    course_name = serializers.CharField(
        max_length=255,
        help_text="Qaysi kursga ariza beryapsiz"
    )
    
    message = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Qo'shimcha xabar (ixtiyoriy)"
    )
    
    class Meta:
        model = Application
        fields = [
            'full_name', 'email', 'phone_number', 
            'course_name', 'message'
        ]
    
    def validate_full_name(self, value):
        """Validate full name"""
        if len(value.split()) < 2:
            raise serializers.ValidationError(
                "Iltimos, ism va familiyangizni to'liq kiriting"
            )
        return value.strip().title()
    
    def validate_course_name(self, value):
        """Validate course name"""
        if not value.strip():
            raise serializers.ValidationError(
                "Kurs nomini kiritish majburiy"
            )
        return value.strip()
    
    def create(self, validated_data):
        """Create application with auto-generated application number"""
        return Application.objects.create(**validated_data)


class ApplicationListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing applications (Admin API)
    """
    status_display = serializers.SerializerMethodField()
    created_at_formatted = serializers.SerializerMethodField()
    application_age = serializers.SerializerMethodField()
    
    class Meta:
        model = Application
        fields = [
            'id', 'application_number', 'full_name', 'email', 
            'phone_number', 'course_name', 'message', 'processed',
            'status_display', 'created_at', 'created_at_formatted', 
            'application_age'
        ]
    
    def get_status_display(self, obj):
        """Get human readable status"""
        return "Qayta ishlangan" if obj.processed else "Kutilmoqda"
    
    def get_created_at_formatted(self, obj):
        """Get formatted creation date"""
        return obj.created_at.strftime('%d.%m.%Y %H:%M')
    
    def get_application_age(self, obj):
        """Get application age in days"""
        from django.utils import timezone
        diff = timezone.now() - obj.created_at
        return diff.days


class ApplicationDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for application details (Admin API)
    """
    status_display = serializers.SerializerMethodField()
    created_at_formatted = serializers.SerializerMethodField()
    application_age = serializers.SerializerMethodField()
    phone_clean = serializers.SerializerMethodField()
    
    class Meta:
        model = Application
        fields = [
            'id', 'application_number', 'full_name', 'email', 
            'phone_number', 'phone_clean', 'course_name', 'message', 
            'processed', 'status_display', 'created_at', 
            'created_at_formatted', 'application_age'
        ]
    
    def get_status_display(self, obj):
        """Get human readable status"""
        return "Qayta ishlangan" if obj.processed else "Kutilmoqda"
    
    def get_created_at_formatted(self, obj):
        """Get formatted creation date"""
        return obj.created_at.strftime('%d.%m.%Y %H:%M')
    
    def get_application_age(self, obj):
        """Get application age in days"""
        from django.utils import timezone
        diff = timezone.now() - obj.created_at
        return diff.days
    
    def get_phone_clean(self, obj):
        """Get clean phone number for calling"""
        return obj.phone_number.replace('+', '').replace(' ', '').replace('-', '')


class ApplicationUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating applications (Admin API)
    """
    class Meta:
        model = Application
        fields = ['processed']
    
    def update(self, instance, validated_data):
        """Update application status"""
        instance.processed = validated_data.get('processed', instance.processed)
        instance.save()
        return instance


class ApplicationStatsSerializer(serializers.Serializer):
    """
    Serializer for application statistics
    """
    total_applications = serializers.IntegerField()
    processed_applications = serializers.IntegerField()
    pending_applications = serializers.IntegerField()
    today_applications = serializers.IntegerField()
    popular_courses = serializers.ListField(
        child=serializers.DictField()
    )
    recent_applications = serializers.ListField(
        child=ApplicationListSerializer()
    )
