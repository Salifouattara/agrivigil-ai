"""Shared Gemini configuration and public errors, without exposing credentials."""
from io import BytesIO

from django.conf import settings
from PIL import Image, UnidentifiedImageError
from rest_framework.exceptions import ValidationError


class AIUnavailableError(RuntimeError):
    pass


def create_gemini_client():
    from google import genai
    if not settings.GEMINI_API_KEY:
        raise AIUnavailableError("Le service IA n'est pas encore configuré.")
    return genai.Client(api_key=settings.GEMINI_API_KEY, http_options={"timeout": 45000})


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
    if isinstance(exc, AIUnavailableError):
        return str(exc), 503
    code = getattr(exc, "code", None)
    if code == 429 or "RESOURCE_EXHAUSTED" in str(exc):
        return "Le quota du service IA est momentanément atteint. Réessaie plus tard.", 429
    return "Le service IA est momentanément indisponible. Réessaie dans quelques instants.", 502
