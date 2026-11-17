import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = "Create the presentation demo account without modifying existing accounts."

    def handle(self, *args, **options):
        User = get_user_model()
        email = "demo@monapp.com"
        if User.objects.filter(email=email).exists():
            self.stdout.write("Demo account already exists; unchanged.")
            return
        password = os.environ.get("DEMO_ACCOUNT_PASSWORD")
        if not password:
            raise CommandError("Set DEMO_ACCOUNT_PASSWORD before creating the demo account.")
        User.objects.create_user(email=email, password=password, full_name="Agriculteur Démo")
        self.stdout.write(self.style.SUCCESS("Demo account created."))
