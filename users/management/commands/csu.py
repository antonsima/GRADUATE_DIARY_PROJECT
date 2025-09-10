import os

from django.core.management import BaseCommand
from dotenv import load_dotenv

from users.models import User

load_dotenv(override=True)


class Command(BaseCommand):
    def handle(self, *args, **options):
        user = User.objects.create(email=os.getenv("TEST_EMAIL"))
        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.set_password(os.getenv("TEST_PASSWORD"))
        user.save()
