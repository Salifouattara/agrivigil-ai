import os
import sys

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from core.models import Expert
from core.serializers import normalize_text, clean_photo_url


for expert in Expert.objects.all():
    expert.name = normalize_text(expert.name)
    expert.role = normalize_text(expert.role)
    expert.specialty = normalize_text(expert.specialty)
    expert.location = normalize_text(expert.location)
    if expert.photo:
        expert.photo.name = clean_photo_url(expert.photo.name)
    expert.save()

print("Expert data cleaned.")
