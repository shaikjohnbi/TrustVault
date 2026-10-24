import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create a one-time Django admin account"

    def handle(self, *args, **options):
        username = os.environ.get("BOOTSTRAP_ADMIN_USERNAME")
        password = os.environ.get("BOOTSTRAP_ADMIN_PASSWORD")

        if not username or not password:
            raise CommandError(
                "Set BOOTSTRAP_ADMIN_USERNAME and "
                "BOOTSTRAP_ADMIN_PASSWORD first."
            )

        User = get_user_model()

        if User.objects.filter(username=username).exists():
            raise CommandError(
                "This username already exists. No changes made."
            )

        User.objects.create_superuser(
            username=username,
            email="",
            password=password,
        )

        self.stdout.write(
            self.style.SUCCESS("Admin account created successfully.")
        )