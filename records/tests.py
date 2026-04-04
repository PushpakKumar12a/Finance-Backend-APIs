from datetime import date, timedelta

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from records.models import Record

class RecordEndpointTests(APITestCase):
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
        cls.viewer = User.objects.create_user(
            email='viewer@example.com',
            username='viewer',
            password='ViewerPass123!',
            role=User.Role.VIEWER,
        )

        cls.record_1 = Record.all_objects.create(
            user=cls.admin,
            amt='1500.00',
            type=Record.TxType.INCOME,
            cat='salary',
            date=date.today() - timedelta(days=10),
            desc='Monthly salary',
        )
        cls.record_2 = Record.all_objects.create(
            user=cls.admin,
            amt='250.00',
            type=Record.TxType.EXPENSE,
            cat='groceries',
            date=date.today() - timedelta(days=5),
            desc='Groceries run',
        )

    def test_viewer_can_list_records(self):
        self.client.force_authenticate(user=self.viewer)

        response = self.client.get(reverse('record-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

    def test_admin_can_create_record(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            reverse('record-list'),
            {
                'amt': '99.99',
                'type': Record.TxType.EXPENSE,
                'cat': 'transport',
                'date': date.today().isoformat(),
                'desc': 'Taxi fare',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Record.all_objects.filter(cat='transport').exists())

    def test_viewer_cannot_create_record(self):
        self.client.force_authenticate(user=self.viewer)

        response = self.client.post(
            reverse('record-list'),
            {
                'amt': '99.99',
                'type': Record.TxType.EXPENSE,
                'cat': 'transport',
                'date': date.today().isoformat(),
                'desc': 'Taxi fare',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_soft_delete_record(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.delete(reverse('record-detail', kwargs={'pk': self.record_1.pk}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.record_1.refresh_from_db()
        self.assertTrue(self.record_1.del_flag)

    def test_filter_by_category_and_amount(self):
        self.client.force_authenticate(user=self.viewer)

        response = self.client.get(reverse('record-list'), {'cat': 'gro', 'amt_min': 200})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['cat'], 'groceries')