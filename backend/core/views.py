import logging
import random
from datetime import date, timedelta

from django.conf import settings
from django.contrib.auth import authenticate
from django.db import transaction
from django.utils import timezone

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from .ai_diagnosis import diagnose_crop_image
from .crop_advice import get_crop_advice_enriched
from .expert_engine import generate_chatbot_reply, generate_expert_reply
from .soil_diagnosis import analyze_soil_image
from .models import CropScan, CropScanTracking, Expert, ExpertMessage, FertilizerCalculation, HealthAlert, OneTimeCode, User
from .serializers import (
    CropScanSerializer, CropScanTrackingSerializer, ExpertMessageSerializer, ExpertSerializer,
    FertilizerCalculationSerializer, ForgotPasswordSerializer, HealthAlertSerializer,
    LoginSerializer, RegisterSerializer, ResetPasswordSerializer, UserSerializer,
    VerifyOtpSerializer,
)
from .utils import TTSServiceError, calculate_fertilizer_detailed, haversine_km, synthesize_text_to_speech
from .weather import IVORIAN_CITIES, get_weather

logger = logging.getLogger(__name__)

OTP_VALIDITY_MINUTES = 15


def _tokens_for(user):
    refresh = RefreshToken.for_user(user)
    return {"access_token": str(refresh.access_token), "refresh_token": str(refresh)}


def _generate_otp(email, purpose):
    code = f"{random.randint(0, 999999):06d}"
    OneTimeCode.objects.create(email=email, code=code, purpose=purpose)
    # MVP : pas d'envoi réel d'email/SMS. On journalise pour la démo.
    # -> Brancher ici Africa's Talking (SMS) ou un service d'email en production.
    print(f"[OTP DEMO] {purpose} pour {email} : {code} (valide {OTP_VALIDITY_MINUTES} min)")
    return code


# ---------------------------------------------------------------------------
# Authentification
# ---------------------------------------------------------------------------

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = User.objects.create_user(
            email=data["email"], password=data["password"],
            full_name=data.get("full_name", ""), is_active=False,
        )
        code = _generate_otp(user.email, "register")
        response = {"detail": "Code de vérification envoyé."}
        if request.data.get("debug"):
            response["debug_otp_code"] = code  # pratique en développement/démo
        return Response(response, status=status.HTTP_201_CREATED)


class VerifyOtpView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = VerifyOtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        code = serializer.validated_data["otp_code"]

        otp = (
            OneTimeCode.objects.filter(email=email, code=code, purpose="register", used=False)
            .order_by("-created_date")
            .first()
        )
        if not otp or timezone.now() - otp.created_date > timedelta(minutes=OTP_VALIDITY_MINUTES):
            return Response({"detail": "Code invalide ou expiré."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "Utilisateur introuvable."}, status=status.HTTP_404_NOT_FOUND)

        otp.used = True
        otp.save(update_fields=["used"])
        user.is_active = True
        user.save(update_fields=["is_active"])

        return Response(_tokens_for(user), status=status.HTTP_200_OK)


class ResendOtpView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"detail": "Email requis."}, status=status.HTTP_400_BAD_REQUEST)
        _generate_otp(email, "register")
        return Response({"detail": "Code renvoyé."})


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        user = authenticate(request, username=email, password=password)
        if not user:
            return Response({"detail": "Identifiants incorrects"}, status=status.HTTP_401_UNAUTHORIZED)
        if not user.is_active:
            return Response({"detail": "Compte non vérifié. Vérifiez votre email."}, status=status.HTTP_403_FORBIDDEN)

        tokens = _tokens_for(user)
        tokens["user"] = UserSerializer(user).data
        return Response(tokens)


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        response = {"detail": "Si un compte existe avec cet email, un lien de réinitialisation a été envoyé."}
        if User.objects.filter(email__iexact=email).exists():
            code = _generate_otp(email, "reset_password")
            if request.data.get("debug"):
                response["debug_reset_token"] = code
        return Response(response)


class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        otp = (
            OneTimeCode.objects.filter(
                email=data["email"], code=data["reset_token"], purpose="reset_password", used=False
            )
            .order_by("-created_date")
            .first()
        )
        if not otp or timezone.now() - otp.created_date > timedelta(minutes=OTP_VALIDITY_MINUTES):
            return Response({"detail": "Lien invalide ou expiré."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=data["email"])
        except User.DoesNotExist:
            return Response({"detail": "Utilisateur introuvable."}, status=status.HTTP_404_NOT_FOUND)

        user.set_password(data["new_password"])
        user.save(update_fields=["password"])
        otp.used = True
        otp.save(update_fields=["used"])
        return Response({"detail": "Mot de passe réinitialisé avec succès."})


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        if refresh_token:
            try:
                RefreshToken(refresh_token).blacklist()
            except Exception:
                pass
        return Response({"detail": "Déconnecté."})


# ---------------------------------------------------------------------------
# Synthèse vocale
# ---------------------------------------------------------------------------

class SynthesizeDioulaView(APIView):
    """Génère un audio TTS à partir d’un texte en français/dioula via Hugging Face."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        text = (request.data.get("text") or "").strip()
        if not text:
            return Response({"detail": "Le texte à synthétiser est requis."}, status=status.HTTP_400_BAD_REQUEST)

        model_name = request.data.get("model_name") or getattr(settings, "HUGGINGFACE_TTS_MODEL", "")
        token = request.data.get("token") or getattr(settings, "HUGGINGFACE_API_TOKEN", "")
        try:
            result = synthesize_text_to_speech(
                text,
                token=token,
                model_name=model_name,
                save_to_storage=True,
            )
        except TTSServiceError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

        return Response({"audio_url": result["audio_url"], "path": result.get("path")}, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# Scan IA
# ---------------------------------------------------------------------------

class CropScanListCreateView(generics.ListCreateAPIView):
    serializer_class = CropScanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CropScan.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CropScanDetailView(generics.DestroyAPIView):
    """
    Permet de supprimer un scan spécifique de l'utilisateur.
    """
    serializer_class = CropScanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CropScan.objects.filter(owner=self.request.user)


class CropScanTrackingListCreateView(generics.ListCreateAPIView):
    serializer_class = CropScanTrackingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CropScanTracking.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CropScanTrackingDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CropScanTrackingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CropScanTracking.objects.filter(owner=self.request.user)


class AnalyzeCropScanView(APIView):
    """
    Reçoit une image de culture, exécute le diagnostic (Gemini 2.5 Flash,
    voir core/ai_diagnosis.py), puis enregistre le CropScan + une HealthAlert
    si une maladie est détectée.
    
    Rejette les images qui ne sont pas des plantes ou des animaux d'élevage valides.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        image = request.FILES.get("image")
        if not image:
            return Response({"detail": "Image requise."}, status=status.HTTP_400_BAD_REQUEST)

        declared_crop = request.data.get("crop_name")
        subject_type = request.data.get("subject_type")  # 'plante' ou 'animal' en frontal
        image_bytes = image.read()
        image.seek(0)
        try:
            # Transmettre la valeur déclarée (culture ou type d'animal) au moteur.
            diagnosis = diagnose_crop_image(image_bytes, declared_crop)
        except Exception as exc:
            exc_text = str(exc)
            if "RESOURCE_EXHAUSTED" in exc_text or "quota" in exc_text.lower() or "429" in exc_text:
                return Response(
                    {
                        "detail": (
                            "Vous n'avez actuellement plus de quota disponible. Le diagnostic IA ne peut pas être lancé pour l'instant. "
                            "Réessaie plus tard."
                        )
                    },
                    status=status.HTTP_502_BAD_GATEWAY,
                )

            return Response(
                {"detail": "Le diagnostic IA a échoué. Vérifie ta configuration API ou réessaie plus tard."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # Valider que l'image contient bien une plante ou un animal reconnus
        if not diagnosis.get("is_valid_subject", False):
            return Response(
                {"detail": "L'image ne contient pas de plante ou d'animal d'élevage reconnu. Veuillez envoyer une image d'une culture ou d'un animal d'élevage."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        lat = request.data.get("location_lat") or None
        lng = request.data.get("location_lng") or None

        tracking = None
        tracking_id = request.data.get("tracking_id")
        new_tracking_name = request.data.get("new_tracking_name")

        if tracking_id:
            try:
                tracking = CropScanTracking.objects.get(id=tracking_id, owner=request.user)
            except (CropScanTracking.DoesNotExist, ValueError):
                pass
        elif new_tracking_name:
            tracking = CropScanTracking.objects.create(
                owner=request.user,
                name=new_tracking_name,
                status="active"
            )

        scan = CropScan.objects.create(
            owner=request.user,
            image=image,
            crop_name=diagnosis["crop_name"],
            # Stocke le type de sujet dans notes si fourni (évite migration DB)
            notes=(subject_type or "plante"),
            disease_name=diagnosis["disease_name"],
            severity=diagnosis["severity"],
            remedy=diagnosis["remedy"],
            dosage=diagnosis["dosage"],
            symptoms=diagnosis["symptoms"],
            prevention=diagnosis["prevention"],
            confidence=diagnosis["confidence"],
            is_healthy=diagnosis["is_healthy"],
            location_lat=lat,
            location_lng=lng,
            status="active",
            tracking=tracking,
        )

        if not diagnosis["is_healthy"]:
            HealthAlert.objects.create(
                reporter=request.user,
                scan=scan,
                disease_name=diagnosis["disease_name"],
                crop_name=diagnosis["crop_name"],
                severity=diagnosis["severity"],
                location_lat=lat,
                location_lng=lng,
                location_label="Votre parcelle",
                image=scan.image,
                status="active",
            )

        response_data = dict(diagnosis)
        response_data["scan_id"] = scan.id
        if tracking:
            response_data["tracking_id"] = tracking.id
            response_data["tracking_name"] = tracking.name
        return Response(response_data, status=status.HTTP_201_CREATED)


# ---------------------------------------------------------------------------
# Alertes sanitaires communautaires
# ---------------------------------------------------------------------------

class HealthAlertListCreateView(generics.ListCreateAPIView):
    serializer_class = HealthAlertSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return HealthAlert.objects.all()[:20]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        user = self.request.user
        distances = {}
        # Distance approximative par rapport au dernier signalement de l'utilisateur,
        # sinon 0. En production : PostGIS + position réelle du dispositif.
        my_last = HealthAlert.objects.filter(reporter=user).order_by("-created_date").first()
        ref_lat, ref_lng = (my_last.location_lat, my_last.location_lng) if my_last else (None, None)
        for alert in self.get_queryset():
            if alert.reporter_id == user.id:
                distances[alert.id] = 0
            else:
                distances[alert.id] = haversine_km(ref_lat, ref_lng, alert.location_lat, alert.location_lng)
        context["distances"] = distances
        return context

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)


class HealthAlertDetailView(generics.RetrieveDestroyAPIView):
    """Récupère ou supprime une alerte. Seul le reporter ou le staff peut supprimer."""
    queryset = HealthAlert.objects.all()
    serializer_class = HealthAlertSerializer
    permission_classes = [permissions.IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        alert = self.get_object()
        if alert.reporter_id != request.user.id and not request.user.is_staff:
            return Response({"detail": "Permission refusée."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


# ---------------------------------------------------------------------------
# Calculateur d'engrais
# ---------------------------------------------------------------------------

class FertilizerCalculationListCreateView(generics.ListCreateAPIView):
    serializer_class = FertilizerCalculationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FertilizerCalculation.objects.filter(owner=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            detailed = calculate_fertilizer_detailed(
                data["crop_type"], data["soil_type"], data["surface_hectares"]
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        record = serializer.save(
            owner=request.user,
            nitrogen_kg=detailed["nitrogen_kg"],
            phosphorus_kg=detailed["phosphorus_kg"],
            potassium_kg=detailed["potassium_kg"],
            recommendation=detailed["recommendation_summary"],
        )

        response_data = FertilizerCalculationSerializer(record, context={"request": request}).data
        response_data.update({
            "products": detailed["products"],
            "total_cost_fcfa": detailed["total_cost_fcfa"],
            "application_plan": detailed["application_plan"],
            "soil_note": detailed["soil_note"],
        })
        return Response(response_data, status=status.HTTP_201_CREATED)


class AnalyzeSoilView(APIView):
    """Analyse une photo de sol pour déterminer le type de texture."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        image = request.FILES.get("image")
        if not image:
            return Response({"detail": "Image requise."}, status=status.HTTP_400_BAD_REQUEST)

        image_bytes = image.read()
        try:
            result = analyze_soil_image(image_bytes)
        except Exception as exc:
            return Response(
                {"detail": f"L'analyse du sol a échoué : {exc}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response(result)


class CropAdviceView(APIView):
    """Conseils agronomiques par culture (pesticides homologués, bonnes pratiques)."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        crop_type = request.query_params.get("crop_type")
        if not crop_type:
            return Response({"detail": "Paramètre crop_type requis."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            advice = get_crop_advice_enriched(crop_type)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(advice)


# ---------------------------------------------------------------------------
# Hub Experts
# ---------------------------------------------------------------------------

class ExpertListView(generics.ListAPIView):
    queryset = Expert.objects.all()
    serializer_class = ExpertSerializer
    # Remplace IsAuthenticated par AllowAny
    permission_classes = [permissions.AllowAny]

class ExpertMessageListCreateView(generics.ListCreateAPIView):
    serializer_class = ExpertMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        conversation_id = self.request.query_params.get("conversation_id")
        qs = ExpertMessage.objects.filter(author=self.request.user).order_by("created_date")
        if conversation_id:
            qs = qs.filter(conversation_id=conversation_id)
        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        conversation_id = serializer.validated_data.get("conversation_id")
        if not conversation_id:
            return Response({"detail": "conversation_id requis."}, status=status.HTTP_400_BAD_REQUEST)

        is_chatbot = conversation_id == "chatbot"
        expert = None
        if not is_chatbot:
            try:
                expert = Expert.objects.get(id=conversation_id)
            except Expert.DoesNotExist:
                return Response({"detail": "Expert introuvable."}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        history = list(
            ExpertMessage.objects.filter(
                author=user,
                conversation_id=conversation_id,
            ).order_by("-created_date")[:10].values("sender_name", "sender_role", "content")
        )
        history.reverse()

        try:
            with transaction.atomic():
                farmer_message = serializer.save(
                    author=user,
                    sender_name=user.full_name or "Agriculteur",
                    sender_role="farmer",
                )
                if is_chatbot:
                    reply_text = generate_chatbot_reply(farmer_message.content, history)
                    expert_name = "Agrivigil IA"
                    conversation_target = "chatbot"
                else:
                    reply_text = generate_expert_reply(expert, farmer_message.content, history)
                    expert_name = expert.name
                    conversation_target = expert.id

                expert_message = ExpertMessage.objects.create(
                    conversation_id=conversation_target,
                    author=user,
                    sender_name=expert_name,
                    sender_role="expert",
                    content=reply_text,
                )
        except Exception as exc:
            logger.exception("Échec génération réponse expert pour %s", conversation_id)
            return Response(
                {"detail": f"La réponse de l'expert a échoué : {exc}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        context = {"request": request}
        return Response(
            {
                "farmer_message": ExpertMessageSerializer(farmer_message, context=context).data,
                "expert_message": ExpertMessageSerializer(expert_message, context=context).data,
            },
            status=status.HTTP_201_CREATED,
        )


# ---------------------------------------------------------------------------
# Météo / Sentinelle Climatique
# ---------------------------------------------------------------------------

class WeatherView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from .weather import WeatherAPIError

        city = request.query_params.get("city", "Abidjan")
        if city not in IVORIAN_CITIES:
            return Response({"detail": "Ville inconnue."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            return Response(get_weather(city, date.today()))
        except WeatherAPIError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_502_BAD_GATEWAY)


class CityListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response([
            {"name": name, "lat": lat, "lon": lon} for name, (lat, lon) in IVORIAN_CITIES.items()
        ])