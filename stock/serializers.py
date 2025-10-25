from rest_framework import serializers  # type: ignore
from .models import Item
from django.utils import timezone


class ItemSerializer(serializers.ModelSerializer):
    in_stock = serializers.ReadOnlyField()
    days_remaining = serializers.SerializerMethodField()
    class Meta:
        fields = '__all__'
        model = Item

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