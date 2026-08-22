from django.core.management.base import BaseCommand

from apps.accounts.constants import ROLE_CHOICES
from apps.accounts.models import User

DEMO_PASSWORD = "demo1234!"


class Command(BaseCommand):
    help = "Crée un utilisateur de test par rôle (mot de passe : demo1234!)."

    def handle(self, *args, **options):
        for role, label in ROLE_CHOICES:
            username = f"demo_{role.lower()}"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": f"{username}@example.org",
                    "role": role,
                    "first_name": label,
                    "is_staff": role == "ADMIN",
                    "is_superuser": role == "ADMIN",
                },
            )
            if created:
                user.set_password(DEMO_PASSWORD)
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Créé : {username} ({label})"))
            else:
                self.stdout.write(f"Déjà existant : {username}")
