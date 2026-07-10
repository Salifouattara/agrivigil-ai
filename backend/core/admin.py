from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import CropScan, Expert, ExpertMessage, FertilizerCalculation, HealthAlert, OneTimeCode, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ["email"]
    list_display = ["email", "full_name", "role", "is_active", "created_date"]
    search_fields = ["email", "full_name"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Informations", {"fields": ("full_name", "role", "phone_number", "preferred_language")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2", "role")}),
    )


@admin.register(CropScan)
class CropScanAdmin(admin.ModelAdmin):
    list_display = ["crop_name", "disease_name", "severity", "owner", "created_date"]
    list_filter = ["severity", "status", "crop_name"]


@admin.register(HealthAlert)
class HealthAlertAdmin(admin.ModelAdmin):
    list_display = ["disease_name", "crop_name", "severity", "location_label", "created_date"]
    list_filter = ["severity", "status"]


@admin.register(FertilizerCalculation)
class FertilizerCalculationAdmin(admin.ModelAdmin):
    list_display = ["crop_type", "soil_type", "surface_hectares", "owner", "created_date"]


@admin.register(Expert)
class ExpertAdmin(admin.ModelAdmin):
    list_display = ["name", "role", "specialty", "location", "phone_number", "whatsapp_number", "online"]
    list_filter = ["role", "online"]
    search_fields = ["name", "specialty", "location", "phone_number"]
    fieldsets = (
        (None, {"fields": ("name", "role", "specialty", "location", "photo", "phone_number", "whatsapp_number", "avatar_color", "online")}),
    )


@admin.register(ExpertMessage)
class ExpertMessageAdmin(admin.ModelAdmin):
    list_display = ["conversation_id", "sender_name", "sender_role", "created_date"]
    search_fields = ["conversation_id", "sender_name", "content"]


admin.site.register(OneTimeCode)
