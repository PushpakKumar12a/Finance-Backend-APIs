from django.core.management.base import BaseCommand
from accounts.models import User

class Command(BaseCommand):
    help = 'Create a default admin user if one does not already exist.'

    def add_arguments(self, parser):
        parser.add_argument('--email', default='admin@finance.local', help='Admin email')
        parser.add_argument('--username', default='admin', help='Admin username')
        parser.add_argument('--password', default='admin123456', help='Admin password')

    def handle(self, *args, **options):
        email = options['email']
        username = options['username']
        password = options['password']

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING(f'Admin user "{email}" already exists.'))
            return

        user = User.objects.create_user(
            email=email,
            username=username,
            password=password,
            role=User.Role.ADMIN,
            is_staff=True,
            is_superuser=True,
        )
        self.stdout.write(self.style.SUCCESS(
            f'Admin user created: {email} / {password}'
        ))
