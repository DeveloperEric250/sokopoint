from django import forms
from .models import Order

class OrderCreateForm(forms.ModelForm):
    quantity = forms.IntegerField(min_value=1, initial=1, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    delivery_address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}))

    class Meta:
        model = Order
        fields = ['delivery_address']


class CheckoutForm(forms.ModelForm):
    PAYMENT_CHOICES = (
        ('MOBILE_MONEY', 'Mobile Money'),
        ('CARD', 'Credit / Debit Card'),
        ('CASH_ON_DELIVERY', 'Cash on Delivery'),
    )
    
    phone_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. +250 788 000 000'}))
    district = forms.ChoiceField(choices=Order.DISTRICT_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    delivery_address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter full delivery address'}))
    payment_method = forms.ChoiceField(choices=PAYMENT_CHOICES, widget=forms.RadioSelect(attrs={'class': 'payment-method-radio'}))

    class Meta:
        model = Order
        fields = ['phone_number', 'district', 'delivery_address']


class CardPaymentForm(forms.Form):
    card_number = forms.CharField(max_length=19, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0000 0000 0000 0000'}))
    expiry = forms.CharField(max_length=5, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'MM/YY'}))
    cvv = forms.CharField(max_length=4, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '123'}))


class MobileMoneyForm(forms.Form):
    PROVIDER_CHOICES = (
        ('MTN', 'MTN Mobile Money'),
        ('AIRTEL', 'Airtel Money'),
        ('MPESA', 'M-Pesa'),
    )
    provider = forms.ChoiceField(choices=PROVIDER_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    phone_number = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 078...'}))
