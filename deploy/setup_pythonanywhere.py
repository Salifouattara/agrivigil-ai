"""Run in a PythonAnywhere Bash console after uploading the release and .env."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

root = Path(__file__).resolve().parents[1]
backend = root / "backend"
venv = root / ".venv"
if not (backend / ".env").is_file():
    raise SystemExit("Missing backend/.env; configure it before installation.")
if not venv.exists():
    subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True)
python = venv / "bin" / "python"
subprocess.run([str(python), "-m", "pip", "install", "--no-cache-dir", "--no-compile", "-r", str(backend / "requirements-pythonanywhere.txt")], check=True)
if (backend / "db.sqlite3").exists():
    import sqlite3
    from datetime import datetime
    backup = backend / ("db-before-" + datetime.now().strftime("%Y%m%d-%H%M%S") + ".sqlite3")
    with sqlite3.connect(backend / "db.sqlite3") as source, sqlite3.connect(backup) as target:
        source.backup(target)
previous = Path.home() / "agrivigil-ai" / "backend"
if not (backend / "db.sqlite3").exists() and (previous / "db.sqlite3").exists():
    import sqlite3
    with sqlite3.connect(previous / "db.sqlite3") as source, sqlite3.connect(backend / "db.sqlite3") as target:
        source.backup(target)
    if (previous / "media").is_dir():
        shutil.copytree(previous / "media", backend / "media", dirs_exist_ok=True)
for command in (["check"], ["migrate", "--noinput"], ["collectstatic", "--noinput"], ["bootstrap_demo"]):
    subprocess.run([str(python), str(backend / "manage.py"), *command], cwd=backend, check=True)
print("AGRIVIGIL_SETUP_OK")
