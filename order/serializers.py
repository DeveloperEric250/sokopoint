from rest_framework import serializers

from product.models import Product
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price']
        read_only_fields = ['id']

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError('Quantity must be greater than zero.')
        return value

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError('Price cannot be negative.')
        return value


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'total_amount', 'status', 'delivery_address', 'district', 'phone_number', 'created_at', 'updated_at', 'order_items']
        read_only_fields = ['id', 'customer', 'created_at', 'updated_at']

    def validate_total_amount(self, value):
        if value < 0:
            raise serializers.ValidationError('Total amount cannot be negative.')
        return value

    def create(self, validated_data):
        order_items_data = validated_data.pop('order_items')
        order = Order.objects.create(**validated_data)
        for item_data in order_items_data:
            OrderItem.objects.create(order=order, **item_data)
        order.total_amount = sum(item['price'] * item['quantity'] for item in order_items_data)
        order.save(update_fields=['total_amount'])
        return order

    def update(self, instance, validated_data):
        order_items_data = validated_data.pop('order_items', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if order_items_data is not None:
            instance.order_items.all().delete()
            for item_data in order_items_data:
                OrderItem.objects.create(order=instance, **item_data)

        return instance
