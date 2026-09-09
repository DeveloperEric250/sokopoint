from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from product.models import Product

from .forms import CustomerUserForm, CustomerRegisterForm, VendorRegisterForm


# Create your views here.
def index(request):
    return HttpResponse("Account app homepage")


def register(request):
    if request.method == 'POST':
        form = CustomerUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('login')
    else:
        form = CustomerUserForm()
    return render(request, 'customer_register.html', {'form': form})


def customer_register(request):
    if request.method == 'POST':
        form = CustomerRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'customer'
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('login')
    else:
        form = CustomerRegisterForm()
    return render(request, 'customer_register.html', {'form': form})


def vendor_register(request):
    if request.method == 'POST':
        form = VendorRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'vendor'
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('login')
    else:
        form = VendorRegisterForm()
    return render(request, 'vendor_register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.user_type == 'vendor':
                return redirect('vendor_dashboard')
            return redirect('customer_dashboard')
        return render(request, 'login.html', {'error': 'invalid username or password'})
    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    return redirect('login')


@login_required
def vendor_dashboard(request):
    if request.user.user_type != 'vendor':
        return HttpResponse('Access denied.')

    products = request.user.products.all()
    return render(request, 'vendor_dashboard.html', {
        'user': request.user,
        'products': products,
    })


@login_required
def customer_dashboard(request):
    if request.user.user_type != 'customer':
        return HttpResponse('Access denied.')

    products = request.user.products.all() if hasattr(request.user, 'products') else []

    if not products:
        products = Product.objects.filter(status=True)

    return render(request, 'customer_dashboard.html', {
        'user': request.user,
        'products': products,
    })


