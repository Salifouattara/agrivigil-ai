import re

from django.contrib.auth import password_validation
from rest_framework import serializers

from .models import CropScan, CropScanTracking, Expert, ExpertMessage, FertilizerCalculation, HealthAlert, User


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
        extra_kwargs = {"image": {"write_only": True, "required": False}}

def get_image_url(self, obj):
        # On renvoie DIRECTEMENT l'URL sans lui coller le domaine de Render devant
        if obj.image:
            return obj.image.url
        return None


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
        # On renvoie DIRECTEMENT l'URL sans lui coller le domaine de Render devant
        if obj.image:
            return obj.image.url
        return None

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
    phone_link = serializers.SerializerMethodField()
    sms_link = serializers.SerializerMethodField()
    whatsapp_link = serializers.SerializerMethodField()
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Expert
        fields = [
            "id", "name", "role", "specialty", "location",
            "phone_number", "whatsapp_number", "phone_link", "sms_link", "whatsapp_link",
            "photo_url", "avatar_color", "online",
        ]

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
        request = self.context.get("request")
        if obj.photo and request:
            return request.build_absolute_uri(obj.photo.url)
        return obj.photo.url if obj.photo else None


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
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url if obj.image else None
