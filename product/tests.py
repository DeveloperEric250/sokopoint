from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class ProductApiTests(APITestCase):
    def setUp(self):
        self.vendor = User.objects.create_user(
            username='vendor-user',
            email='vendor@example.com',
            password='StrongPass123!',
            user_type='vendor',
        )
        self.client.force_authenticate(user=self.vendor)

    def test_create_and_list_products(self):
        url = reverse('product-list')
        payload = {
            'name': 'Rice Bag',
            'price': '25.50',
            'currency': 'RWF',
            'description': 'High quality rice',
            'unit': 'kg',
            'status': True,
        }

        create_response = self.client.post(url, payload, format='json')

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(create_response.data['name'], 'Rice Bag')

        list_response = self.client.get(url)
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(list_response.data['results']), 0)

    def test_negative_price_is_rejected(self):
        url = reverse('product-list')
        payload = {
            'name': 'Bad Product',
            'price': '-5.00',
            'currency': 'USD',
            'description': 'Invalid',
            'unit': 'pcs',
            'status': True,
        }

        response = self.client.post(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('price', response.data)
