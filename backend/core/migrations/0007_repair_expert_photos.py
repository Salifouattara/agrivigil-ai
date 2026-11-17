from django.db import migrations

IDS = ("plant_issouf", "plant_mariam", "vet_awa", "vet_yao")

def repair_photos(apps, schema_editor):
    Expert = apps.get_model("core", "Expert")
    for expert in Expert.objects.filter(id__in=IDS):
        name = str(expert.photo or "")
        if not name or name.startswith("experts/photos/Capture"):
            expert.photo = f"experts/photos/{expert.id}.png"
            expert.save(update_fields=["photo"])

class Migration(migrations.Migration):
    dependencies = [("core", "0006_load_initial_experts")]
    operations = [migrations.RunPython(repair_photos, migrations.RunPython.noop)]
