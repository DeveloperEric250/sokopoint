from django.contrib import admin
# pyrefly: ignore [missing-import]
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'vendor', 'price', 'currency', 'unit', 'status', 'created_at']
    list_filter = ['status', 'currency', 'unit', 'created_at']
    search_fields = ['name', 'vendor__username', 'description']
