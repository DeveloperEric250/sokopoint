from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from product.models import Product

User = get_user_model()


class OrderApiTests(APITestCase):
    def setUp(self):
        self.vendor = User.objects.create_user(
            username='vendor-order',
            email='vendor-order@example.com',
            password='StrongPass123!',
            user_type='vendor',
        )
        self.customer = User.objects.create_user(
            username='customer-order',
            email='customer-order@example.com',
            password='StrongPass123!',
            user_type='customer',
        )
        self.product = Product.objects.create(
            vendor=self.vendor,
            name='Beans',
            price='12.00',
            currency='RWF',
            description='Fresh beans',
            unit='kg',
            status=True,
        )

    def test_customer_can_create_order(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('order-list')
        payload = {
            'customer': self.customer.id,
            'total_amount': '12.00',
            'status': 'PENDING',
            'delivery_address': 'Kigali',
            'district': 'KICUKIRO',
            'phone_number': '250788111222',
            'order_items': [
                {
                    'product': self.product.id,
                    'quantity': 1,
                    'price': '12.00',
                }
            ],
        }

        response = self.client.post(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['customer'], self.customer.id)
        self.assertEqual(len(response.data['order_items']), 1)

    def test_vendor_can_view_orders_for_their_products(self):
        self.client.force_authenticate(user=self.vendor)
        url = reverse('order-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
