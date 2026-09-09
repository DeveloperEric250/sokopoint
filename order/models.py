from django.db import models


class Order(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    )

    DISTRICT_CHOICES = (
        ('BUGESERA', 'Bugesera'),
        ('BURERA', 'Burera'),
        ('GAKENKE', 'Gakenke'),
        ('GASABO', 'Gasabo'),
        ('GATSIBO', 'Gatsibo'),
        ('GISAGARA', 'Gisagara'),
        ('HUYE', 'Huye'),
        ('KAMONYI', 'Kamonyi'),
        ('KARONGI', 'Karongi'),
        ('KAYONZA', 'Kayonza'),
        ('KICUKIRO', 'Kicukiro'),
        ('KIREHE', 'Kirehe'),
        ('MUHANGA', 'Muhanga'),
        ('MUSANZE', 'Musanze'),
        ('NGOMA', 'Ngoma'),
        ('NGORORERO', 'Ngororero'),
        ('NYABIHU', 'Nyabihu'),
        ('NYAGATARE', 'Nyagatare'),
        ('NYAMAGABE', 'Nyamagabe'),
        ('NYAMASHEKE', 'Nyamasheke'),
        ('NYANZA', 'Nyanza'),
        ('NYARUGENGE', 'Nyarugenge'),
        ('RULINDO', 'Rulindo'),
        ('RUSIZI', 'Rusizi'),
        ('RUHANGO', 'Ruhango'),
        ('RUBAVU', 'Rubavu'),
        ('RWAMAGANA', 'Rwamagana'),
        ('GICUMBI', 'Gicumbi'),
        ('RUTSIRO', 'Rutsiro'),
        ('NYARUGURU', 'Nyaruguru'),
    )

    customer = models.ForeignKey('account.CustomUser', on_delete=models.CASCADE, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    delivery_address = models.TextField(blank=True, null=True)
    district = models.CharField(max_length=30, choices=DISTRICT_CHOICES, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Order {self.id} by {self.customer.username}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey('product.Product', on_delete=models.CASCADE, related_name='order_items')
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.quantity} of {self.product.name} in {self.order.id}'


class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('MOBILE_MONEY', 'Mobile Money'),
        ('CARD', 'Credit/Debit Card'),
        ('CASH_ON_DELIVERY', 'Cash on Delivery'),
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    transaction_reference = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Payment {self.id} for order {self.order.id}'