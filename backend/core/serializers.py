import re
import urllib.parse
import unicodedata

from django.conf import settings
from django.contrib.auth import password_validation
from rest_framework import serializers

from .models import CropScan, CropScanTracking, Expert, ExpertMessage, FertilizerCalculation, HealthAlert, User


MOJIBAKE_REPLACEMENTS = {
    "Ã¯Â¿Â½": "é",
    "Ã©": "é",
    "Ã¨": "è",
    "Ãª": "ê",
    "Ã«": "ë",
    "Ã§": "ç",
    "Ã¸": "ø",
    "Ã¶": "ö",
    "Ã´": "ô",
    "Ã¼": "ü",
    "Ã¹": "ù",
    "Ã»": "û",
    "Ã¢": "â",
    "Ã®": "î",
    "Ã¯": "ï",
    "Ã‰": "É",
    "Ãˆ": "È",
    "ÃŠ": "Ê",
    "Ã‹": "Ë",
    "Ã‡": "Ç",
    "Ã–": "Ö",
    "Ãœ": "Ü",
    "Ã€": "À",
    "Ã‚": "Â",
    "Ã„": "Ä",
    "Ã…": "Å",
    "Ãƒ": "Ã",
}


def normalize_text(value):
    if not isinstance(value, str):
        return value

    normalized = value
    for bad, good in MOJIBAKE_REPLACEMENTS.items():
        normalized = normalized.replace(bad, good)

    normalized = normalized.replace("%EF%BF%BD", "")
    normalized = normalized.replace("�", "")
    normalized = unicodedata.normalize("NFKD", normalized)
    normalized = "".join(char for char in normalized if not unicodedata.combining(char))
    normalized = normalized.encode("ascii", "ignore").decode("ascii")
    normalized = re.sub(r"[^A-Za-z0-9\s_-]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def clean_photo_url(value):
    if not isinstance(value, str) or not value:
        return value

    cleaned = value.strip().replace("%EF%BF%BD", "").replace("�", "")
    cleaned = re.sub(r"https?:/res\.cloudinary\.com/", "https://res.cloudinary.com/", cleaned)

    if cleaned.startswith(("http://", "https://")):
        if "res.cloudinary.com/" in cleaned:
            parts = re.split(r"https?://res\.cloudinary\.com/", cleaned)
            if len(parts) > 1:
                suffix = parts[-1].lstrip("/")
                cleaned = f"https://res.cloudinary.com/{suffix}"

        parsed = urllib.parse.urlsplit(cleaned)
        if parsed.scheme and parsed.netloc:
            path = urllib.parse.unquote(parsed.path)
            path = re.sub(r"[^A-Za-z0-9/._-]", "", path)
            if not any(path.lower().endswith(ext) for ext in (".jpg", ".jpeg", ".png", ".avif")):
                path = f"{path}.avif"
            return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, path, parsed.query, parsed.fragment))
        return cleaned

    normalized_path = cleaned.lstrip("/")
    if normalized_path.startswith("res.cloudinary.com/"):
        normalized_path = normalized_path.split("res.cloudinary.com/", 1)[1]

    if not any(normalized_path.lower().endswith(ext) for ext in (".jpg", ".jpeg", ".png", ".avif")):
        normalized_path = f"{normalized_path}.avif"

    return f"https://res.cloudinary.com/gymzkxvk/{normalized_path.lstrip('/')}"


def media_file_url(field, request=None):
    if not field:
        return None
    name = getattr(field, "name", "")
    if name.startswith(("http://", "https://")):
        return clean_photo_url(name) if "res.cloudinary.com/" in name else name
    url = field.url
    return request.build_absolute_uri(url) if request else url


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "full_name", "role", "phone_number", "preferred_language", "created_date"]
        read_only_fields = ["id", "role", "created_date"]


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    full_name = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Un compte existe déjà avec cet email.")
        return value

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value


class VerifyOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6, min_length=6)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    reset_token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        password_validation.validate_password(value)
        return value


class CropScanTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CropScanTracking
        fields = ["id", "name", "status", "created_date", "updated_date"]
        read_only_fields = ["id", "created_date", "updated_date"]


class CropScanSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    tracking_id = serializers.PrimaryKeyRelatedField(
        queryset=CropScanTracking.objects.all(),
        source="tracking",
        required=False,
        allow_null=True
    )

    class Meta:
        model = CropScan
        fields = [
            "id", "image", "image_url", "crop_name", "disease_name", "severity",
            "remedy", "dosage", "symptoms", "prevention", "confidence", "is_healthy",
            "notes", "location_lat", "location_lng", "status", "created_date", "tracking_id"
        ]
        read_only_fields = ["id", "created_date"]

    def get_image(self, obj):
        return media_file_url(obj.image, self.context.get("request"))

    def get_image_url(self, obj):
        return self.get_image(obj)


class HealthAlertSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    distance_km = serializers.SerializerMethodField()
    # Si l'alerte est liée à un `CropScan`, exposer ses détails utiles
    scan = CropScanSerializer(read_only=True)
    prevention = serializers.SerializerMethodField()
    remedy = serializers.SerializerMethodField()

    class Meta:
        model = HealthAlert
        fields = [
            "id", "image", "image_url", "disease_name", "crop_name", "severity",
            "location_lat", "location_lng", "location_label", "status",
            "distance_km", "created_date", "scan", "prevention", "remedy",
        ]
        read_only_fields = ["id", "created_date"]
        extra_kwargs = {"image": {"write_only": True, "required": False}}

    def get_image_url(self, obj):
        if not obj.image:
            return None

        return media_file_url(obj.image, self.context.get("request"))

    def get_distance_km(self, obj):
        # Calculé côté vue (haversine) et injecté dans le contexte ; 0 par défaut
        # pour les alertes de l'utilisateur courant.
        distances = self.context.get("distances", {})
        return distances.get(obj.id, 0)

    def get_prevention(self, obj):
        if obj.scan:
            return obj.scan.prevention
        return ""

    def get_remedy(self, obj):
        if obj.scan:
            return obj.scan.remedy
        return ""


class FertilizerCalculationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FertilizerCalculation
        fields = [
            "id", "crop_type", "soil_type", "surface_hectares",
            "nitrogen_kg", "phosphorus_kg", "potassium_kg", "recommendation", "created_date",
        ]
        read_only_fields = ["id", "nitrogen_kg", "phosphorus_kg", "potassium_kg", "recommendation", "created_date"]


class ExpertSerializer(serializers.ModelSerializer):
    is_demo = serializers.SerializerMethodField()
    phone_link = serializers.SerializerMethodField()
    sms_link = serializers.SerializerMethodField()
    whatsapp_link = serializers.SerializerMethodField()
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Expert
        fields = [
            "id", "name", "role", "specialty", "location",
            "phone_number", "whatsapp_number", "phone_link", "sms_link", "whatsapp_link",
            "photo_url", "avatar_color", "online", "is_demo",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        for field_name in ("name", "role", "specialty", "location"):
            value = representation.get(field_name)
            if isinstance(value, str):
                representation[field_name] = normalize_text(value)
        return representation

    def get_is_demo(self, obj):
        return obj.id in {"plant_issouf", "plant_mariam", "vet_awa", "vet_yao"}

    def get_phone_link(self, obj):
        return f"tel:{obj.phone_number}" if obj.phone_number else None

    def get_sms_link(self, obj):
        return f"sms:{obj.phone_number}" if obj.phone_number else None

    def get_whatsapp_link(self, obj):
        phone = obj.whatsapp_number or obj.phone_number
        if not phone:
            return None
        normalized = re.sub(r"\D", "", phone)
        return f"https://wa.me/{normalized}"

    def get_photo_url(self, obj):
        if not obj.photo:
            return None

        return media_file_url(obj.photo, self.context.get("request"))


class ExpertMessageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ExpertMessage
        fields = [
            "id", "conversation_id", "sender_name", "sender_role",
            "content", "image", "image_url", "scan", "created_date",
        ]
        read_only_fields = ["id", "sender_name", "sender_role", "created_date"]
        extra_kwargs = {"image": {"write_only": True, "required": False}}

    def get_image_url(self, obj):
        if not obj.image:
            return None

        return media_file_url(obj.image, self.context.get("request"))
