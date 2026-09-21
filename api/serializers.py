import re
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from product.models import Product
from order.models import Order, OrderItem, Payment

User = get_user_model()


# ──────────────────────────────────────────────
# AUTH SERIALIZERS
# ──────────────────────────────────────────────

class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration with validation."""
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True, label="Confirm password")

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'phone', 'location',
            'user_type', 'first_name', 'last_name',
            'password', 'password2',
        ]
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate_email(self, value):
        """Email must be unique."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_phone(self, value):
        """Phone number must be valid (digits, optional + prefix, 10-15 chars)."""
        if value:
            pattern = r'^\+?[0-9]{10,15}$'
            if not re.match(pattern, value):
                raise serializers.ValidationError(
                    "Phone number must be 10-15 digits, optionally starting with '+'."
                )
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Passwords do not match."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password."""
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(
        required=True, write_only=True, validators=[validate_password]
    )
    new_password2 = serializers.CharField(required=True, write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError(
                {"new_password": "New passwords do not match."}
            )
        return attrs


# ──────────────────────────────────────────────
# USER / PROFILE SERIALIZERS
# ──────────────────────────────────────────────

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for viewing and updating user profile."""

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'phone', 'location',
            'user_type', 'first_name', 'last_name', 'date_joined',
        ]
        read_only_fields = ['id', 'username', 'user_type', 'date_joined']


# ──────────────────────────────────────────────
# PRODUCT SERIALIZERS
# ──────────────────────────────────────────────

class ProductSerializer(serializers.ModelSerializer):
    """Full Product serializer with validation."""
    vendor_username = serializers.CharField(source='vendor.username', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'vendor', 'vendor_username', 'name', 'price', 'currency',
            'description', 'unit', 'image', 'status', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'vendor', 'vendor_username', 'created_at', 'updated_at']

    def validate_price(self, value):
        """Price cannot be negative."""
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        return value


# ──────────────────────────────────────────────
# ORDER SERIALIZERS (Nested)
# ──────────────────────────────────────────────

class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for individual order items."""
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price']
        read_only_fields = ['id', 'price']


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payments."""

    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'amount', 'status', 'payment_method',
            'transaction_reference', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'order', 'amount', 'transaction_reference',
            'created_at', 'updated_at',
        ]


class OrderSerializer(serializers.ModelSerializer):
    """Order serializer with nested OrderItems and Payments."""
    order_items = OrderItemSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    customer_username = serializers.CharField(source='customer.username', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'customer_username', 'total_amount', 'status',
            'delivery_address', 'district', 'phone_number',
            'created_at', 'updated_at',
            'order_items', 'payments',
        ]
        read_only_fields = [
            'id', 'customer', 'customer_username', 'total_amount',
            'created_at', 'updated_at',
        ]


class OrderCreateSerializer(serializers.Serializer):
    """Serializer for creating an order with items."""
    delivery_address = serializers.CharField()
    district = serializers.ChoiceField(choices=Order.DISTRICT_CHOICES)
    phone_number = serializers.CharField(max_length=20)
    payment_method = serializers.ChoiceField(
        choices=Payment.PAYMENT_METHOD_CHOICES
    )
    items = OrderItemSerializer(many=True)

    def validate_phone_number(self, value):
        pattern = r'^\+?[0-9]{10,15}$'
        if not re.match(pattern, value):
            raise serializers.ValidationError(
                "Phone number must be 10-15 digits, optionally starting with '+'."
            )
        return value

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Order must have at least one item.")
        return value

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        payment_method = validated_data.pop('payment_method')
        user = self.context['request'].user

        # Calculate total
        total = 0
        for item in items_data:
            product = item['product']
            total += product.price * item['quantity']

        order = Order.objects.create(
            customer=user,
            total_amount=total,
            **validated_data,
        )

        for item in items_data:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['product'].price,
            )

        Payment.objects.create(
            order=order,
            amount=total,
            payment_method=payment_method,
            status='PENDING',
        )

        return order
