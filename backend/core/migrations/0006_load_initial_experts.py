import json
from pathlib import Path

from django.db import migrations


def _load_json_with_fallback(json_path):
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            with json_path.open("r", encoding=encoding) as fh:
                return json.load(fh)
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
    raise UnicodeDecodeError("utf-8", b"", 0, 1, "Unable to decode experts_data.json")


def load_experts_from_json(apps, schema_editor):
    Expert = apps.get_model("core", "Expert")
    json_path = Path(__file__).resolve().parent.parent.parent / "experts_data.json"

    if not json_path.exists():
        return

    data = _load_json_with_fallback(json_path)

    for entry in data:
        if entry.get("model") != "core.expert":
            continue

        pk = entry.get("pk")
        fields = entry.get("fields", {})

        Expert.objects.get_or_create(
            id=pk,
            defaults={
                "name": fields.get("name", ""),
                "role": fields.get("role", ""),
                "specialty": fields.get("specialty", ""),
                "location": fields.get("location", ""),
                "phone_number": fields.get("phone_number", ""),
                "whatsapp_number": fields.get("whatsapp_number", ""),
                "photo": fields.get("photo", ""),
                "avatar_color": fields.get("avatar_color", "#2D5A3D"),
                "online": fields.get("online", True),
            },
        )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0005_alter_cropscan_dosage"),
    ]

    operations = [
        migrations.RunPython(load_experts_from_json, migrations.RunPython.noop),
    ]
