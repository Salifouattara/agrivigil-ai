from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    # Auth
    path("auth/register/", views.RegisterView.as_view(), name="register"),
    path("auth/verify-otp/", views.VerifyOtpView.as_view(), name="verify-otp"),
    path("auth/resend-otp/", views.ResendOtpView.as_view(), name="resend-otp"),
    path("auth/login/", views.LoginView.as_view(), name="login"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("auth/me/", views.MeView.as_view(), name="me"),
    path("auth/logout/", views.LogoutView.as_view(), name="logout"),
    path("auth/forgot-password/", views.ForgotPasswordView.as_view(), name="forgot-password"),
    path("auth/reset-password/", views.ResetPasswordView.as_view(), name="reset-password"),

    # Synthèse vocale
    path("synthesize-dioula/", views.SynthesizeDioulaView.as_view(), name="synthesize-dioula"),

    # Scan IA
    path("scans/", views.CropScanListCreateView.as_view(), name="scan-list-create"),
    path("scans/<uuid:pk>/", views.CropScanDetailView.as_view(), name="scan-detail"),
    path("scans/analyze/", views.AnalyzeCropScanView.as_view(), name="scan-analyze"),
    path("trackings/", views.CropScanTrackingListCreateView.as_view(), name="tracking-list-create"),
    path("trackings/<uuid:pk>/", views.CropScanTrackingDetailView.as_view(), name="tracking-detail"),

    # Alertes sanitaires
    path("alerts/", views.HealthAlertListCreateView.as_view(), name="alert-list-create"),
    path("alerts/<uuid:pk>/", views.HealthAlertDetailView.as_view(), name="alert-detail"),

    # Calculateur d'engrais
    path("calculator/", views.FertilizerCalculationListCreateView.as_view(), name="calculator-list-create"),
    path("calculator/analyze-soil/", views.AnalyzeSoilView.as_view(), name="calculator-analyze-soil"),

    # Conseils agronomiques
    path("advice/", views.CropAdviceView.as_view(), name="crop-advice"),

    # Hub Experts
    path("experts/", views.ExpertListView.as_view(), name="expert-list"),
    path("experts/messages/", views.ExpertMessageListCreateView.as_view(), name="expert-message-list-create"),

    # Météo
    path("weather/", views.WeatherView.as_view(), name="weather"),
    path("weather/cities/", views.CityListView.as_view(), name="weather-cities"),
]
