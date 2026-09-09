from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from product.models import Product
from .models import Order, OrderItem, Payment
from .forms import OrderCreateForm, CheckoutForm, CardPaymentForm, MobileMoneyForm
from cart.cart import Cart
import uuid

# Create your views here.
def index(request):
    return HttpResponse('Order app homepage')


@login_required
def place_order(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            delivery_address = form.cleaned_data['delivery_address']
            
            total_amount = product.price * quantity

            order = Order.objects.create(
                customer=request.user,
                total_amount=total_amount,
                delivery_address=delivery_address,
            )

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price,
            )

            messages.success(request, 'Order placed successfully!')
            return render(request, 'order_success.html', {'order': order, 'product': product})
    else:
        form = OrderCreateForm()

    return render(request, 'place_order.html', {'product': product, 'form': form})


@login_required
def customer_orders(request):
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'customer_orders.html', {'orders': orders})


@login_required
def vendor_orders(request):
    orders = Order.objects.filter(order_items__product__vendor=request.user).distinct().order_by('-created_at')
    return render(request, 'vendor_orders.html', {'orders': orders})


@login_required
@require_POST
def confirm_order(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        order_items__product__vendor=request.user,
    )

    if order.status == 'PROCESSING':
        order.status = 'SHIPPED'
        order.save(update_fields=['status', 'updated_at'])
        messages.success(request, f'Order #{order.id} confirmed and marked as shipped.')
    else:
        messages.info(request, f'Order #{order.id} cannot be confirmed from its current status.')

    return redirect('vendor_orders')


@login_required
def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, "Your cart is empty. Please add items before checking out.")
        return redirect('cart_detail')
        
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Create Order
            order = form.save(commit=False)
            order.customer = request.user
            order.total_amount = cart.get_total_price()
            order.status = 'PENDING'
            order.save()
            
            # Create Order Items
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    quantity=item['quantity'],
                    price=item['price']
                )
                
            # Create pending Payment record
            Payment.objects.create(
                order=order,
                amount=order.total_amount,
                payment_method=form.cleaned_data['payment_method'],
                status='PENDING'
            )
            
            return redirect('process_payment', order_id=order.id)
    else:
        form = CheckoutForm(initial={
            'phone_number': request.user.phone or '',
            'delivery_address': request.user.location or '',
        })
        
    return render(request, 'checkout.html', {'form': form, 'cart': cart})


@login_required
def process_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    payment = get_object_or_404(Payment, order=order)
    
    if payment.status == 'COMPLETED':
        return redirect('order_confirmation', order_id=order.id)
        
    if payment.payment_method == 'CASH_ON_DELIVERY':
        # Instantly complete COD
        payment.status = 'COMPLETED'
        payment.save()
        order.status = 'PROCESSING'
        order.save()
        
        # Clear Cart
        cart = Cart(request)
        cart.clear()
        
        messages.success(request, 'Order placed successfully!')
        return redirect('order_confirmation', order_id=order.id)
        
    if request.method == 'POST':
        if payment.payment_method == 'CARD':
            form = CardPaymentForm(request.POST)
        else:
            form = MobileMoneyForm(request.POST)
            
        if form.is_valid():
            # Simulate payment processing success
            payment.status = 'COMPLETED'
            payment.transaction_reference = str(uuid.uuid4())[:18]
            payment.save()
            
            order.status = 'PROCESSING'
            order.save()
            
            # Clear Cart
            cart = Cart(request)
            cart.clear()
            
            messages.success(request, 'Payment processed successfully!')
            return redirect('order_confirmation', order_id=order.id)
    else:
        if payment.payment_method == 'CARD':
            form = CardPaymentForm()
        else:
            form = MobileMoneyForm()
            
    return render(request, 'payment.html', {'order': order, 'payment': payment, 'form': form})


@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    return render(request, 'order_confirmation.html', {'order': order})

