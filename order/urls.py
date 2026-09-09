from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='order_index'),
    path('place/<int:product_id>/', views.place_order, name='place_order'),
    path('customer/', views.customer_orders, name='customer_orders'),
    path('vendor/', views.vendor_orders, name='vendor_orders'),
    path('vendor/confirm/<int:order_id>/', views.confirm_order, name='confirm_order'),
    
    # New Advanced Checkout URLs
    path('checkout/', views.checkout, name='checkout'),
    path('payment/<int:order_id>/', views.process_payment, name='process_payment'),
    path('confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
]
