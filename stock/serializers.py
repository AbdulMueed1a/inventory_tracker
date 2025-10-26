from rest_framework import serializers  # type: ignore
from .models import Item
from django.utils import timezone
from datetime import date


class ItemSerializer(serializers.ModelSerializer):
    in_stock = serializers.SerializerMethodField()
    days_remaining = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = (
            'id',
            'name',
            'price',
            'added',
            'expiry',
            'quantity',
            'low_stock',
            'in_stock',
            'days_remaining',
            'is_expired',
        )
        read_only_fields = ('id', 'added', 'in_stock', 'days_remaining', 'is_expired')

    def get_in_stock(self, obj):
        try:
            return bool(getattr(obj, 'quantity', 0) and getattr(obj, 'quantity', 0) > 0)
        except Exception:
            return False

    def get_days_remaining(self, obj):
        """
        Returns integer days remaining until expiry (0 if expired or no expiry).
        """
        expiry = getattr(obj, 'expiry', None)
        if expiry is None:
            return None
        # expiry may be date or datetime
        try:
            today = timezone.localdate() if hasattr(timezone, 'localdate') else date.today()
        except Exception:
            today = date.today()
        if hasattr(expiry, 'date'):
            expiry_date = expiry.date()
        else:
            expiry_date = expiry
        try:
            delta = (expiry_date - today).days
            return max(delta, 0)
        except Exception:
            return None

    def get_is_expired(self, obj):
        expiry = getattr(obj, 'expiry', None)
        if expiry is None:
            return False
        try:
            today = timezone.localdate() if hasattr(timezone, 'localdate') else date.today()
        except Exception:
            today = date.today()
        if hasattr(expiry, 'date'):
            expiry_date = expiry.date()
        else:
            expiry_date = expiry
        try:
            return expiry_date < today
        except Exception:
            return False

    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative.")
        return value

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        return value

    def validate_expiry_date(self, value):
        if value and value < timezone.localdate():
            raise serializers.ValidationError("Expiry date cannot be in the past.")
        return value


    def validate(self, attrs):
        expiry = attrs.get('expiry_date')
        quantity = attrs.get('quantity', None)
        if expiry and expiry <= timezone.localdate() and quantity and quantity > 0:
            raise serializers.ValidationError("Cannot stock already-expired items.")
        return attrs