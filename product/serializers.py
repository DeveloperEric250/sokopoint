from rest_framework import serializers

from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id',
            'vendor',
            'name',
            'price',
            'currency',
            'description',
            'unit',
            'image',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'vendor', 'created_at', 'updated_at']

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError('Price cannot be negative.')
        return value
