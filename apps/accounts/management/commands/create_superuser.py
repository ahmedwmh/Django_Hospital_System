from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.accounts.models import User


class Command(BaseCommand):
    help = 'Create a superuser with admin role'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Email address')
        parser.add_argument('--username', type=str, help='Username')
        parser.add_argument('--password', type=str, help='Password')
        parser.add_argument('--first-name', type=str, help='First name')
        parser.add_argument('--last-name', type=str, help='Last name')

    def handle(self, *args, **options):
        email = options['email'] or 'admin@hospital.com'
        username = options['username'] or 'admin'
        password = options['password'] or 'admin123'
        first_name = options['first_name'] or 'Admin'
        last_name = options['last_name'] or 'User'

        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(f'User with email {email} already exists')
            )
            return

        user = User.objects.create_superuser(
            email=email,
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role='ADMIN'
        )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created superuser: {user.email}')
        )
