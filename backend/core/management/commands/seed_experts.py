from django.core.management.base import BaseCommand

from core.models import Expert

EXPERTS = [
    {
        "id": "plant_issouf", "name": "Dr. Issouf Touré", "role": "Médecin de plantes",
        "specialty": "Phytopathologie, maladies du cacao et café", "location": "Abidjan",
        "avatar_color": "#2D5A3D", "online": True,
    },
    {
        "id": "plant_mariam", "name": "Dr. Mariam Cissé", "role": "Médecin de plantes",
        "specialty": "Cultures vivrières, fertilisation et ravageurs", "location": "Yamoussoukro",
        "avatar_color": "#3D7A52", "online": True,
    },
    {
        "id": "vet_awa", "name": "Dr. Awa Koné", "role": "Vétérinaire",
        "specialty": "Élevage bovin et ovin", "location": "Bouaké",
        "avatar_color": "#C97B3D", "online": True,
    },
    {
        "id": "vet_yao", "name": "Dr. Yao Kouassi", "role": "Vétérinaire",
        "specialty": "Volailles et porcins", "location": "Korhogo",
        "avatar_color": "#B84A3E", "online": True,
    },
]


class Command(BaseCommand):
    help = "Crée les experts simulés du Hub Experts (idempotent)."

    def handle(self, *args, **options):
        for data in EXPERTS:
            expert, created = Expert.objects.update_or_create(id=data["id"], defaults=data)
            action = "créé" if created else "mis à jour"
            self.stdout.write(self.style.SUCCESS(f"Expert {action} : {expert.name}"))
