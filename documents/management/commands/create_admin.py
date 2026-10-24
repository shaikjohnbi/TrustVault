
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create or reset the deployment admin account"

    def handle(self, *args, **options):
        username = os.environ.get("BOOTSTRAP_ADMIN_USERNAME")
        password = os.environ.get("BOOTSTRAP_ADMIN_PASSWORD")

        if not username or not password:
            raise CommandError(
                "Bootstrap admin environment variables are missing."
            )

        User = get_user_model()
        user = User.objects.filter(username=username).first()

        if user is None:
            User.objects.create_superuser(
                username=username,
                email="",
                password=password,
            )
            self.stdout.write(
                self.style.SUCCESS("Admin account created successfully.")
            )
        else:
            user.set_password(password)
            user.is_active = True
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(
                self.style.SUCCESS("Admin password reset successfully.")
            )
