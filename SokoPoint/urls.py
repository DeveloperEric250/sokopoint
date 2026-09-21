"""
URL configuration for SokoPoint project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include('account.urls')),
    path('product/', include('product.urls')),
    path('order/', include('order.urls')),
    path('cart/', include('cart.urls')),
    path('api/', include('api.urls')),
    path('', views.home, name='home'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
