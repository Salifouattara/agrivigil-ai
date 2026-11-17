import os
import sys
from pathlib import Path
from dotenv import load_dotenv

backend = Path.home() / "agrivigil-release-20261117" / "backend"
sys.path.insert(0, str(backend))
load_dotenv(backend / ".env")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
