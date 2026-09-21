from django import forms
# pyrefly: ignore [missing-import]
from .models import Product


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = [
            'name',
            'price',
            'currency',
            'description',
            'unit',
            'image',
            'status',
        ]