from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class AccountApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='demo-user',
            email='demo@example.com',
            password='StrongPass123!',
            first_name='Demo',
            last_name='User',
            phone='250788123456',
            location='Kigali',
            user_type='customer',
        )

    def test_register_user_returns_tokens(self):
        url = reverse('api_register')
        payload = {
            'username': 'new_user',
            'email': 'new_user@example.com',
            'phone': '250788654321',
            'location': 'Kigali',
            'user_type': 'vendor',
            'password': 'VeryStrongPass123!',
            'confirm_password': 'VeryStrongPass123!',
        }

        response = self.client.post(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])

    def test_login_returns_jwt_tokens(self):
        url = reverse('api_login')
        payload = {
            'username': 'demo-user',
            'password': 'StrongPass123!',
        }

        response = self.client.post(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_profile_and_change_password(self):
        url = reverse('api_profile')
        change_password_url = reverse('change_password')
        self.client.force_authenticate(user=self.user)

        get_response = self.client.get(url)
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(get_response.data['username'], 'demo-user')

        patch_response = self.client.patch(url, {'first_name': 'Updated', 'location': 'Huye'}, format='json')
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_response.data['first_name'], 'Updated')

        password_response = self.client.post(
            change_password_url,
            {
                'old_password': 'StrongPass123!',
                'new_password': 'NewStrongPass456!',
                'confirm_password': 'NewStrongPass456!',
            },
            format='json',
        )
        self.assertEqual(password_response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewStrongPass456!'))
