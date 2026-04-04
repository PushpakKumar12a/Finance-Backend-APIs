from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import User
from records.models import Record


class Command(BaseCommand):
    help = 'Seed demo users (admin, analyst, viewers) and sample financial records.'

    def handle(self, *args, **options):
        with transaction.atomic():
            admin_user = self._get_or_create_user(
                email='admin@finance.local',
                username='admin',
                password='admin123456',
                role=User.Role.ADMIN,
                is_staff=True,
                is_superuser=True,
            )

            analyst_user = self._get_or_create_user(
                email='analyst@finance.local',
                username='analyst',
                password='analyst123456',
                role=User.Role.ANALYST,
                is_staff=False,
                is_superuser=False,
            )

            viewer_user = self._get_or_create_user(
                email='viewer@finance.local',
                username='viewer',
                password='viewer123456',
                role=User.Role.VIEWER,
                is_staff=False,
                is_superuser=False,
            )

            sample_records = [
                {
                    'user': admin_user,
                    'amt': '8500.00',
                    'type': Record.TxType.INCOME,
                    'cat': 'salary',
                    'date': date.today() - timedelta(days=25),
                    'desc': 'Monthly salary',
                },
                {
                    'user': analyst_user,
                    'amt': '2400.00',
                    'type': Record.TxType.INCOME,
                    'cat': 'consulting',
                    'date': date.today() - timedelta(days=18),
                    'desc': 'Consulting payment',
                },
                {
                    'user': viewer_user,
                    'amt': '1250.00',
                    'type': Record.TxType.EXPENSE,
                    'cat': 'rent',
                    'date': date.today() - timedelta(days=14),
                    'desc': 'Apartment rent',
                },
                {
                    'user': viewer_user,
                    'amt': '180.50',
                    'type': Record.TxType.EXPENSE,
                    'cat': 'groceries',
                    'date': date.today() - timedelta(days=10),
                    'desc': 'Weekly groceries',
                },
                {
                    'user': analyst_user,
                    'amt': '320.00',
                    'type': Record.TxType.EXPENSE,
                    'cat': 'transport',
                    'date': date.today() - timedelta(days=7),
                    'desc': 'Fuel and transit',
                },
                {
                    'user': admin_user,
                    'amt': '950.00',
                    'type': Record.TxType.EXPENSE,
                    'cat': 'equipment',
                    'date': date.today() - timedelta(days=3),
                    'desc': 'Work equipment purchase',
                },
            ]

            created_records = 0
            for record_data in sample_records:
                record, created = Record.all_objects.get_or_create(
                    user=record_data['user'],
                    amt=record_data['amt'],
                    type=record_data['type'],
                    cat=record_data['cat'],
                    date=record_data['date'],
                    desc=record_data['desc'],
                    defaults={'del_flag': False},
                )
                if not created and record.del_flag:
                    record.del_flag = False
                    record.save(update_fields=['del_flag', 'updated_at'])
                if created:
                    created_records += 1

            self.stdout.write(self.style.SUCCESS(
                'Seeded demo data: '
                f'admin={admin_user.email}, analyst={analyst_user.email}, viewer={viewer_user.email}, '
                f'new_records={created_records}'
            ))

    def _get_or_create_user(self, email, username, password, role, is_staff, is_superuser):
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': username,
                'role': role,
                'is_staff': is_staff,
                'is_superuser': is_superuser,
            },
        )

        if created:
            user.set_password(password)
            user.save()
            return user

        needs_save = False
        if user.username != username:
            user.username = username
            needs_save = True
        if user.role != role:
            user.role = role
            needs_save = True
        if user.is_staff != is_staff:
            user.is_staff = is_staff
            needs_save = True
        if user.is_superuser != is_superuser:
            user.is_superuser = is_superuser
            needs_save = True
        if not user.check_password(password):
            user.set_password(password)
            needs_save = True
        if needs_save:
            user.save()
        return user