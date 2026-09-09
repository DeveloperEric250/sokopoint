from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from .form import ProductForm
from .models import Product
from django.contrib.auth.decorators import login_required
# Create your views here.


def index(request):
    return HttpResponse("Product app homepage")



@login_required
def add_product(request):

    if request.user.user_type != 'vendor':
        return redirect('customer_dashboard')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            product = form.save(commit=False)

            product.vendor = request.user

            product.save()

            return redirect('vendor_dashboard')

    else:
        form = ProductForm()

    return render(request, 'product/add_product.html', {
        'form': form
    })


@login_required
def product_list(request):
    if request.user.user_type == 'vendor':
        products = Product.objects.filter(vendor=request.user)
    else:
        products = Product.objects.all()

    return render(request, 'product_list.html', {
        'products': products
    })


@login_required
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    return render(request, 'product/product_detail.html', {
        'product': product
    })


@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.user.user_type != 'vendor' or product.vendor != request.user:
        return redirect('vendor_dashboard')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('vendor_dashboard')
    else:
        form = ProductForm(instance=product)

    return render(request, 'product_edit.html', {'form': form, 'product': product})


@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.user.user_type != 'vendor' or product.vendor != request.user:
        return redirect('vendor_dashboard')

    if request.method == 'POST':
        product.delete()
        return redirect('vendor_dashboard')

    return render(request, 'product_delete.html', {'product': product})
