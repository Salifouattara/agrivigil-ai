import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _


# ---------------------------------------------------------------------------
# Utilisateur
# ---------------------------------------------------------------------------

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'email est obligatoire")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("role", "admin")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [("admin", "Administrateur"), ("user", "Utilisateur")]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, verbose_name=_("email"))
    full_name = models.CharField(max_length=150, blank=True, verbose_name=_("nom complet"))
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="user", verbose_name=_("rôle"))
    phone_number = models.CharField(max_length=20, blank=True, verbose_name=_("téléphone"))
    preferred_language = models.CharField(
        max_length=20,
        choices=[
            ("fr", "Français"),
            ("dioula", "Dioula"),
            ("baoule", "Baoulé"),
            ("bete", "Bété"),
            ("senoufo", "Sénoufo"),
        ],
        default="fr",
        verbose_name=_("langue préférée"),
    )
    is_active = models.BooleanField(default=True, verbose_name=_("actif"))
    is_staff = models.BooleanField(default=False, verbose_name=_("membre du staff"))
    created_date = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "users"
        verbose_name = _("Utilisateur")
        verbose_name_plural = _("Utilisateurs")

    def __str__(self):
        return self.email


class OneTimeCode(models.Model):
    """Code de vérification à 6 chiffres pour l'inscription et la réinitialisation du mot de passe."""

    PURPOSE_CHOICES = [("register", "Inscription"), ("reset_password", "Réinitialisation")]

    email = models.EmailField()
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    created_date = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    class Meta:
        db_table = "one_time_codes"
        verbose_name = _("Code à usage unique")
        verbose_name_plural = _("Codes à usage unique")


# ---------------------------------------------------------------------------
# Modèle de base horodaté (comme les entités Base44 : created_date / updated_date)
# ---------------------------------------------------------------------------

class TimeStampedModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_date"]


# ---------------------------------------------------------------------------
# CropScanTracking — suivi de santé d'une culture ou animal spécifique
# ---------------------------------------------------------------------------

class CropScanTracking(TimeStampedModel):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("resolved", "Résolue"),
    ]
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="trackings")
    name = models.CharField(max_length=150)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")

    class Meta(TimeStampedModel.Meta):
        db_table = "crop_scan_trackings"
        verbose_name = _("Suivi de culture/animal")
        verbose_name_plural = _("Suivis de cultures/animaux")

    def __str__(self):
        return self.name


# ---------------------------------------------------------------------------
# CropScan — résultat d'un scan IA d'une culture
# ---------------------------------------------------------------------------

class CropScan(TimeStampedModel):
    SEVERITY_CHOICES = [
        ("faible", "Faible"),
        ("modérée", "Modérée"),
        ("élevée", "Élevée"),
        ("critique", "Critique"),
    ]
    STATUS_CHOICES = [("active", "Active"), ("treated", "Traitée"), ("resolved", "Résolue")]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="scans")
    tracking = models.ForeignKey(
        "CropScanTracking",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="scans"
    )
    image = models.ImageField(upload_to="scans/%Y/%m/")
    crop_name = models.CharField(max_length=100)
    disease_name = models.CharField(max_length=150, blank=True)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default="faible")
    remedy = models.TextField(blank=True)
    dosage = models.CharField(max_length=255, blank=True)
    symptoms = models.TextField(blank=True)
    prevention = models.TextField(blank=True)
    confidence = models.FloatField(default=0)
    is_healthy = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    location_lat = models.FloatField(null=True, blank=True)
    location_lng = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")

    class Meta(TimeStampedModel.Meta):
        db_table = "crop_scans"
        verbose_name = _("Scan de culture")
        verbose_name_plural = _("Scans de culture")


# ---------------------------------------------------------------------------
# HealthAlert — alerte communautaire (foyer de maladie signalé)
# ---------------------------------------------------------------------------

class HealthAlert(TimeStampedModel):
    SEVERITY_CHOICES = CropScan.SEVERITY_CHOICES
    STATUS_CHOICES = [("active", "Active"), ("traitée", "Traitée")]

    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="alerts")
    scan = models.ForeignKey(CropScan, on_delete=models.SET_NULL, null=True, blank=True, related_name="alerts")
    disease_name = models.CharField(max_length=150)
    crop_name = models.CharField(max_length=100)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default="modérée")
    location_lat = models.FloatField(null=True, blank=True)
    location_lng = models.FloatField(null=True, blank=True)
    location_label = models.CharField(max_length=150, blank=True)
    image = models.ImageField(upload_to="alerts/%Y/%m/", blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")

    class Meta(TimeStampedModel.Meta):
        db_table = "health_alerts"
        verbose_name = _("Alerte sanitaire")
        verbose_name_plural = _("Alertes sanitaires")


# ---------------------------------------------------------------------------
# FertilizerCalculation — historique des calculs d'engrais
# ---------------------------------------------------------------------------

class FertilizerCalculation(TimeStampedModel):
    CROP_CHOICES = [
        ("cacao", "Cacao"), ("café", "Café"), ("manioc", "Manioc"), ("riz", "Riz"),
        ("maïs", "Maïs"), ("igname", "Igname"), ("banane_plantain", "Banane plantain"),
        ("hévéa", "Hévéa"), ("palmier_huile", "Palmier à huile"), ("coton", "Coton"),
    ]
    SOIL_CHOICES = [
        ("argileux", "Argileux"), ("sableux", "Sableux"), ("limoneux", "Limoneux"),
        ("latéritique", "Latéritique"), ("tourbeux", "Tourbeux"),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="calculations")
    crop_type = models.CharField(max_length=30, choices=CROP_CHOICES)
    soil_type = models.CharField(max_length=20, choices=SOIL_CHOICES)
    surface_hectares = models.FloatField()
    nitrogen_kg = models.FloatField()
    phosphorus_kg = models.FloatField()
    potassium_kg = models.FloatField()
    recommendation = models.TextField(blank=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "fertilizer_calculations"
        verbose_name = _("Calcul d'engrais")
        verbose_name_plural = _("Calculs d'engrais")


# ---------------------------------------------------------------------------
# Expert — annuaire des experts (agronomes / vétérinaires) simulés pour le MVP
# ---------------------------------------------------------------------------

class Expert(models.Model):
    ROLE_CHOICES = [("Médecin de plantes", "Médecin de plantes"), ("Vétérinaire", "Vétérinaire")]

    id = models.SlugField(primary_key=True, max_length=50)
    name = models.CharField(max_length=150, verbose_name=_("nom"))
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, verbose_name=_("rôle"))
    specialty = models.CharField(max_length=200, verbose_name=_("spécialité"))
    location = models.CharField(max_length=100, verbose_name=_("localisation"))
    phone_number = models.CharField(max_length=20, blank=True, verbose_name=_("téléphone"))
    whatsapp_number = models.CharField(max_length=20, blank=True, verbose_name=_("WhatsApp"))
    photo = models.ImageField(upload_to="experts/photos/", blank=True, null=True, verbose_name=_("photo"))
    avatar_color = models.CharField(max_length=10, default="#2D5A3D", verbose_name=_("couleur avatar"))
    online = models.BooleanField(default=True, verbose_name=_("en ligne"))

    class Meta:
        db_table = "experts"
        verbose_name = _("Expert")
        verbose_name_plural = _("Experts")

    def __str__(self):
        return self.name


class ExpertMessage(TimeStampedModel):
    ROLE_CHOICES = [("farmer", "Agriculteur"), ("expert", "Expert")]

    conversation_id = models.CharField(max_length=50, db_index=True)  # = Expert.id
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="expert_messages")
    sender_name = models.CharField(max_length=150)
    sender_role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="farmer")
    content = models.TextField()
    image = models.ImageField(upload_to="expert_chat/%Y/%m/", blank=True, null=True)
    scan = models.ForeignKey(CropScan, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta(TimeStampedModel.Meta):
        db_table = "expert_messages"
        ordering = ["created_date"]
        verbose_name = _("Message expert")
        verbose_name_plural = _("Messages experts")
