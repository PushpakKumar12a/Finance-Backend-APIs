from decimal import Decimal
from datetime import date, timedelta
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from records.models import Record

class DashboardEndpointTests(APITestCase):
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
        cls.viewer = User.objects.create_user(
            email='viewer@example.com',
            username='viewer',
            password='ViewerPass123!',
            role=User.Role.VIEWER,
        )

        Record.all_objects.create(
            user=cls.admin,
            amt='3000.00',
            type=Record.TxType.INCOME,
            cat='salary',
            date=date.today() - timedelta(days=20),
            desc='Salary',
        )
        Record.all_objects.create(
            user=cls.analyst,
            amt='500.00',
            type=Record.TxType.EXPENSE,
            cat='groceries',
            date=date.today() - timedelta(days=10),
            desc='Groceries',
        )
        Record.all_objects.create(
            user=cls.viewer,
            amt='1200.00',
            type=Record.TxType.EXPENSE,
            cat='rent',
            date=date.today() - timedelta(days=2),
            desc='Rent',
        )

    def test_viewer_cannot_access_dashboard(self):
        self.client.force_authenticate(user=self.viewer)

        response = self.client.get(reverse('dashboard-summary'))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_analyst_can_access_summary(self):
        self.client.force_authenticate(user=self.analyst)

        response = self.client.get(reverse('dashboard-summary'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(str(response.data['inc'])), Decimal('3000.00'))
        self.assertEqual(Decimal(str(response.data['exp'])), Decimal('1700.00'))
        self.assertEqual(Decimal(str(response.data['net'])), Decimal('1300.00'))
        self.assertEqual(response.data['recs'], 3)

    def test_dashboard_category_breakdown(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(reverse('dashboard-category-breakdown'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        categories = {(item['cat'], item['type']) for item in response.data}
        self.assertIn(('salary', 'income'), categories)
        self.assertIn(('groceries', 'expense'), categories)
        self.assertIn(('rent', 'expense'), categories)

    def test_dashboard_recent_activity_limits_to_ten(self):
        for index in range(11):
            Record.all_objects.create(
                user=self.admin,
                amt='10.00',
                type=Record.TxType.EXPENSE,
                cat=f'cat-{index}',
                date=date.today() - timedelta(days=index),
                desc=f'entry-{index}',
            )

        self.client.force_authenticate(user=self.admin)

        response = self.client.get(reverse('dashboard-recent-activity'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 10)