"""Create a source-only release. Secrets, databases and uploaded images stay local."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

root = Path(__file__).resolve().parents[1]
output = root / ".local" / "agrivigil-pythonanywhere.zip"
output.parent.mkdir(exist_ok=True)
files = list((root / "backend" / "config").rglob("*.py")) + list((root / "backend" / "core").rglob("*.py"))
files += [root / "backend" / name for name in ("manage.py", "experts_data.json", "requirements-pythonanywhere.txt")]
files += list((root / "deploy").glob("*.py"))
files += [root / "backend/media/experts/photos" / f"{name}.png" for name in ("plant_issouf", "plant_mariam", "vet_awa", "vet_yao")]
with ZipFile(output, "w", ZIP_DEFLATED) as archive:
    for file in files:
        if "__pycache__" not in file.parts:
            archive.write(file, file.relative_to(root).as_posix())
print(f"Release prepared: {output.name} ({output.stat().st_size // 1024} KiB)")
