"""
Franchise application serializers
"""
from rest_framework import serializers
from apps.franchise.models import FranchiseApplication


class FranchiseApplicationSerializer(serializers.ModelSerializer):
    """
    Full serializer for franchise applications (admin use)
    """
    formatted_investment_amount = serializers.ReadOnlyField()
    is_pending = serializers.ReadOnlyField()
    is_approved = serializers.ReadOnlyField()

    class Meta:
        model = FranchiseApplication
        fields = [
            'id',
            'full_name',
            'phone',
            'email',
            'city',
            'investment_amount',
            'formatted_investment_amount',
            'experience',
            'message',
            'status',
            'is_pending',
            'is_approved',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_phone(self, value):
        """Validate phone number format"""
        if not value.strip():
            raise serializers.ValidationError("Phone number is required.")
        
        # Basic phone validation - you can make this more sophisticated
        cleaned_phone = ''.join(char for char in value if char.isdigit() or char in '+()-. ')
        if len(cleaned_phone.replace(' ', '').replace('+', '').replace('-', '').replace('(', '').replace(')', '')) < 10:
            raise serializers.ValidationError("Phone number must be at least 10 digits.")
        
        return value

    def validate_investment_amount(self, value):
        """Validate investment amount"""
        if value <= 0:
            raise serializers.ValidationError("Investment amount must be greater than 0.")
        
        if value > 10000000:  # 10 million limit
            raise serializers.ValidationError("Investment amount cannot exceed $10,000,000.")
        
        return value


class FranchiseApplicationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for public franchise application creation
    Only accepts user input fields, status is always set to 'pending'
    """
    
    class Meta:
        model = FranchiseApplication
        fields = [
            'full_name',
            'phone',
            'email',
            'city',
            'investment_amount',
            'experience',
            'message',
        ]

    def validate_phone(self, value):
        """Validate phone number format"""
        if not value.strip():
            raise serializers.ValidationError("Phone number is required.")
        
        # Basic phone validation
        cleaned_phone = ''.join(char for char in value if char.isdigit() or char in '+()-. ')
        if len(cleaned_phone.replace(' ', '').replace('+', '').replace('-', '').replace('(', '').replace(')', '')) < 10:
            raise serializers.ValidationError("Phone number must be at least 10 digits.")
        
        return value

    def validate_investment_amount(self, value):
        """Validate investment amount"""
        if value <= 0:
            raise serializers.ValidationError("Investment amount must be greater than 0.")
        
        if value > 10000000:  # 10 million limit
            raise serializers.ValidationError("Investment amount cannot exceed $10,000,000.")
        
        return value

    def validate_full_name(self, value):
        """Validate full name"""
        if not value.strip():
            raise serializers.ValidationError("Full name is required.")
        
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Full name must be at least 2 characters long.")
        
        return value.strip()

    def validate_city(self, value):
        """Validate city"""
        if not value.strip():
            raise serializers.ValidationError("City is required.")
        
        if len(value.strip()) < 2:
            raise serializers.ValidationError("City must be at least 2 characters long.")
        
        return value.strip()

    def create(self, validated_data):
        """Create franchise application with pending status"""
        # Always set status to pending for public submissions
        validated_data['status'] = 'pending'
        return super().create(validated_data)


class FranchiseApplicationListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing franchise applications (admin use)
    Provides essential information for listing views
    """
    formatted_investment_amount = serializers.ReadOnlyField()
    is_pending = serializers.ReadOnlyField()
    is_approved = serializers.ReadOnlyField()

    class Meta:
        model = FranchiseApplication
        fields = [
            'id',
            'full_name',
            'phone',
            'city',
            'investment_amount',
            'formatted_investment_amount',
            'status',
            'is_pending',
            'is_approved',
            'created_at',
        ]
