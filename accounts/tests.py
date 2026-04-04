from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User

class AccountEndpointTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(
            email='admin@example.com',
            username='admin',
            password='AdminPass123!',
            role=User.Role.ADMIN,
            is_staff=True,
            is_superuser=True,
        )
        cls.analyst = User.objects.create_user(
            email='analyst@example.com',
            username='analyst',
            password='AnalystPass123!',
            role=User.Role.ANALYST,
        )

    def test_register_creates_viewer_user(self):
        response = self.client.post(
            reverse('auth-register'),
            {
                'email': 'viewer@example.com',
                'username': 'viewer',
                'password': 'ViewerPass123!',
                'password_confirm': 'ViewerPass123!',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['role'], User.Role.VIEWER)
        self.assertTrue(User.objects.filter(email='viewer@example.com').exists())

    def test_login_returns_tokens(self):
        response = self.client.post(
            reverse('auth-login'),
            {
                'email': self.admin.email,
                'password': 'AdminPass123!',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_profile_requires_authentication(self):
        self.client.force_authenticate(user=self.analyst)

        response = self.client.get(reverse('auth-profile'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.analyst.email)

    def test_admin_can_list_users(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(reverse('user-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['count'], 2)

    def test_analyst_cannot_list_users(self):
        self.client.force_authenticate(user=self.analyst)

        response = self.client.get(reverse('user-list'))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_promote_user_to_analyst(self):
        viewer = User.objects.create_user(
            email='viewer2@example.com',
            username='viewer2',
            password='ViewerPass123!',
        )
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            reverse('user-detail', kwargs={'pk': viewer.pk}),
            {'role': User.Role.ANALYST},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        viewer.refresh_from_db()
        self.assertEqual(viewer.role, User.Role.ANALYST)