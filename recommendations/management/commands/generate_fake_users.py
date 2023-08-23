from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from faker import Faker
from authentication.models import CustomUser
from authentication.utils import create_user_account

class Command(BaseCommand):
    help = 'Generate fake users'

    def handle(self, *args, **options):
        User = get_user_model()
        fake = Faker()

        num_users = 1000 # Set the desired number of fake users (current amount of users = 504)
        if num_users <= 0: 
            pass
        for _ in range(num_users):
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = fake.email()
            password = fake.password()

            user = create_user_account(email, password, first_name=first_name, last_name=last_name)
            self.stdout.write(self.style.SUCCESS(f'Successfully created user: {user}'))
