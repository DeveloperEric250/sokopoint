from django.db import models


# Create your models here.
class Product(models.Model):
    CURRENCY_CHOICES = [
        ('USD', 'USD ($)'),
        ('RWF', 'RWF (Fr)'),
        ('EUR', 'EUR (€)'),
        ('KES', 'KES (KSh)'),
    ]

    UNIT_CHOICES = [
        ("kg", "Kilogram"),
        ("g", "Gram"),
        ("pcs", "Pieces"),
        ("lit", "Litre"),
        ("ml", "Millilitre"),
        ("m", "Metre"),
        ("cm", "Centimetre"),
        ("mm", "Millimetre"),
        ("inch", "Inch"),
        ("foot", "Foot"),
        ("yard", "Yard"),
        ("bag", "Bag"),
        ("box", "Box"),
        ("crate", "Crate"),
        ("bunch", "Bunch"),
    ]

    vendor = models.ForeignKey('account.CustomUser', on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES, default='USD')
    description = models.TextField()
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='pcs')
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    