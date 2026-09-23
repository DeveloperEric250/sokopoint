from rest_framework import permissions, viewsets

from .models import Product
from .serializers import ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.user_type == 'vendor':
            return Product.objects.filter(vendor=self.request.user).order_by('-created_at')
        return Product.objects.filter(status=True).order_by('-created_at')

    def perform_create(self, serializer):
        if self.request.user.user_type != 'vendor':
            raise permissions.PermissionDenied('Only vendors can create products.')
        serializer.save(vendor=self.request.user)

    def perform_update(self, serializer):
        if self.request.user.user_type != 'vendor' or serializer.instance.vendor != self.request.user:
            raise permissions.PermissionDenied('You can only update your own products.')
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user.user_type != 'vendor' or instance.vendor != self.request.user:
            raise permissions.PermissionDenied('You can only delete your own products.')
        instance.delete()
