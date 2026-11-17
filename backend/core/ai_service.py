"""Shared Gemini configuration and public errors, without exposing credentials."""
from io import BytesIO
import logging
import time

from django.conf import settings
from PIL import Image, UnidentifiedImageError
from requests.exceptions import ConnectionError, Timeout
from rest_framework.exceptions import ValidationError

logger = logging.getLogger(__name__)


class AIUnavailableError(RuntimeError):
    pass


def create_gemini_client():
    from google import genai
    if not settings.GEMINI_API_KEY:
        raise AIUnavailableError("Le service IA n'est pas encore configuré.")
    return genai.Client(api_key=settings.GEMINI_API_KEY, http_options={"timeout": 45000})


def run_ai_request(request):
    """Retry one transient provider failure; never retry quota or invalid input."""
    try:
        return request()
    except Exception as exc:
        code = getattr(exc, "code", None)
        if not isinstance(exc, (ConnectionError, Timeout)) and code not in {500, 502, 503, 504}:
            raise
        # Log metadata only: provider messages can contain credentials or user data.
        logger.warning("Retrying AI request: error=%s code=%s", type(exc).__name__, code)
        time.sleep(1)
        return request()


def image_mime_type(data):
    try:
        with Image.open(BytesIO(data)) as image:
            mime = Image.MIME.get(image.format)
            image.verify()
        if mime not in {"image/jpeg", "image/png", "image/webp"}:
            raise ValueError("unsupported format")
        return mime
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
        raise ValidationError({"detail": "Choisis une image JPEG, PNG ou WebP valide."}) from None


def read_uploaded_image(image):
    if image.size > 10 * 1024 * 1024:
        raise ValidationError({"detail": "L'image doit peser moins de 10 Mo."})
    data = image.read()
    image.seek(0)
    image_mime_type(data)
    return data


def public_ai_error(exc):
    logger.error("AI request failed: error=%s code=%s", type(exc).__name__, getattr(exc, "code", None))
    if isinstance(exc, AIUnavailableError):
        return str(exc), 503
    code = getattr(exc, "code", None)
    if code == 429 or "RESOURCE_EXHAUSTED" in str(exc):
        return "Le quota du service IA est momentanément atteint. Réessaie plus tard.", 429
    return "Le service IA est momentanément indisponible. Réessaie dans quelques instants.", 502
