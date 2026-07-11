import os

from django.core.management.base import BaseCommand, CommandError

from core.models import CropScan
from core.utils import ensure_image_extension


class Command(BaseCommand):
    help = "Corrige les URLs d’image tronquées des CropScan en ajoutant une extension si nécessaire."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Affiche les changements sans les sauvegarder")
        parser.add_argument("--default-extension", default="avif", help="Extension par défaut si aucune n’est détectée")

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        default_extension = options["default_extension"].lstrip(".")

        scans = CropScan.objects.exclude(image__isnull=True).exclude(image="")
        count = scans.count()
        updated = 0

        self.stdout.write(self.style.WARNING(f"{count} CropScan(s) à vérifier..."))

        for scan in scans:
            current_value = scan.image.name if scan.image else ""
            if not current_value:
                continue

            new_value = ensure_image_extension(current_value, default_extension=default_extension)
            if new_value != current_value:
                updated += 1
                self.stdout.write(
                    self.style.WARNING(f"- {scan.id}: {current_value} -> {new_value}")
                )
                if not dry_run:
                    scan.image.name = new_value
                    scan.save(update_fields=["image"])

        if dry_run:
            self.stdout.write(self.style.SUCCESS(f"Aperçu terminé : {updated} correction(s) proposée(s)."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Nettoyage terminé : {updated} correction(s) enregistrée(s)."))
