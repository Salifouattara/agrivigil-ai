from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from core.models import CropScan, HealthAlert


ALERTS = [
    {
        "crop_name": "cacao",
        "disease_name": "Pourriture brune des cabosses (Phytophthora)",
        "severity": "élevée",
        "symptoms": "Taches brunes étendues sur les cabosses, parfois duvet blanchâtre.",
        "remedy": "Retirer cabosses atteintes et appliquer bouillie bordelaise en prévention.",
        "dosage": "Bouillie bordelaise 0,5% : 2,5 kg pour 500 L d'eau/ha, 3 applications.",
        "prevention": "Élaguer pour aérer la cacaoyère et éviter l'excès d'humidité.",
        "location_label": "Région d'Abidjan",
        "location_lat": 5.348,
        "location_lng": -4.008,
    },
    {
        "crop_name": "riz",
        "disease_name": "Pyriculariose du riz (Magnaporthe oryzae)",
        "severity": "élevée",
        "symptoms": "Taches gris-brun en losange sur les feuilles.",
        "remedy": "Appliquer fongicide systémique (triazole) dès les premières taches.",
        "dosage": "Selon notice du produit, 0,5 à 1 L/ha en 2 applications.",
        "prevention": "Éviter l'excès d'azote et assurer un bon drainage.",
        "location_label": "Région d'Abidjan",
        "location_lat": 5.348,
        "location_lng": -4.008,
    },
    {
        "crop_name": "manioc",
        "disease_name": "Mosaïque africaine du manioc",
        "severity": "critique",
        "symptoms": "Feuilles mosaïquées, déformation et réduction du feuillage.",
        "remedy": "Arracher plants atteints et utiliser boutures certifiées saines.",
        "dosage": "Pas de traitement chimique efficace — lutte variétale.",
        "prevention": "Rotation des cultures et lutte contre les vecteurs (mouche blanche).",
        "location_label": "Région d'Abidjan",
        "location_lat": 5.348,
        "location_lng": -4.008,
    },
]


class Command(BaseCommand):
    help = "Crée des alertes sanitaires codées (idempotent)."

    def handle(self, *args, **options):
        User = get_user_model()
        system_user, created = User.objects.get_or_create(
            email="system@local",
            defaults={"full_name": "Système", "is_active": True},
        )
        if created:
            self.stdout.write(self.style.SUCCESS("Utilisateur système créé : system@local"))

        for idx, a in enumerate(ALERTS, start=1):
            scan_data = dict(
                owner=system_user,
                crop_name=a["crop_name"],
                disease_name=a["disease_name"],
                severity=a["severity"],
                remedy=a["remedy"],
                dosage=a["dosage"],
                symptoms=a["symptoms"],
                prevention=a["prevention"],
                confidence=90.0,
                is_healthy=False,
                location_lat=a.get("location_lat"),
                location_lng=a.get("location_lng"),
            )
            scan, screated = CropScan.objects.update_or_create(
                crop_name=scan_data["crop_name"], disease_name=scan_data["disease_name"], defaults=scan_data
            )
            alert, acreated = HealthAlert.objects.update_or_create(
                disease_name=a["disease_name"], crop_name=a["crop_name"], defaults={
                    "reporter": system_user,
                    "scan": scan,
                    "severity": a["severity"],
                    "location_lat": a.get("location_lat"),
                    "location_lng": a.get("location_lng"),
                    "location_label": a.get("location_label"),
                    "status": "active",
                }
            )
            action = "créée" if acreated else "mise à jour"
            self.stdout.write(self.style.SUCCESS(f"Alerte {action} : {alert.disease_name} ({alert.location_label})"))
