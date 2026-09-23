from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Order, OrderItem
from .serializers import OrderSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'vendor':
            return Order.objects.filter(order_items__product__vendor=user).distinct().order_by('-created_at')
        return Order.objects.filter(customer=user).order_by('-created_at')

    def perform_create(self, serializer):
        if self.request.user.user_type != 'customer':
            raise permissions.PermissionDenied('Only customers can create orders.')
        serializer.save(customer=self.request.user)

    @action(detail=True, methods=['patch'], url_path='mark-as-processed')
    def mark_as_processed(self, request, *args, **kwargs):
        order = self.get_object()
        if request.user.user_type != 'vendor' or not order.order_items.filter(product__vendor=request.user).exists():
            raise permissions.PermissionDenied('You can only update orders for your products.')

        order.status = 'PROCESSING'
        order.save(update_fields=['status', 'updated_at'])
        serializer = self.get_serializer(order)
        return Response(serializer.data)


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'vendor':
            return OrderItem.objects.filter(product__vendor=user)
        return OrderItem.objects.filter(order__customer=user)

    def perform_create(self, serializer):
        serializer.save()

