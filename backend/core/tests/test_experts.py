from django.test import SimpleTestCase, override_settings

from core.models import Expert
from core.serializers import ExpertSerializer, clean_photo_url, normalize_text


class ExpertSerializerTests(SimpleTestCase):
    def test_serializer_normalizes_mojibake_expert_fields(self):
        expert = Expert(
            id="plant_issouf",
            name="Dr. Issouf TourÃ¯Â¿Â½",
            role="MÃ¯Â¿Â½decin de plantes",
            specialty="Phytopathologie, maladies du cacao et cafÃ¯Â¿Â½",
            location="Abidjan",
        )

        data = ExpertSerializer(expert).data

        self.assertEqual(data["name"], "Dr Issouf Toure")
        self.assertEqual(data["role"], "Medecin de plantes")
        self.assertEqual(data["specialty"], "Phytopathologie maladies du cacao et cafe")
        self.assertEqual(data["location"], "Abidjan")

    def test_normalize_text_removes_accents_and_special_chars(self):
        self.assertEqual(normalize_text("Cissé, Dr. Touré"), "Cisse Dr Toure")

    def test_clean_photo_url_removes_mojibake_sequences(self):
        url = "https://res.cloudinary.com/demo/image/upload/experts/photos/Capture_d%EF%BF%BDcran_2026-07-09_084039.png"
        self.assertEqual(
            clean_photo_url(url),
            "https://res.cloudinary.com/demo/image/upload/experts/photos/Capture_dcran_2026-07-09_084039.png",
        )

    def test_clean_photo_url_recovers_from_double_cloudinary_prefix(self):
        url = "https://res.cloudinary.com/gymzkxvk/image/upload/v1783760669/https:/res.cloudinary.com/gymzkxvk/scans/2026/07/FLI-LSD-Klinik-Kopf_original_web_liv_j5qfen.avif"
        self.assertEqual(
            clean_photo_url(url),
            "https://res.cloudinary.com/gymzkxvk/scans/2026/07/FLI-LSD-Klinik-Kopf_original_web_liv_j5qfen.avif",
        )

    @override_settings(MEDIA_URL="https://res.cloudinary.com/demo/")
    def test_clean_photo_url_prefixes_relative_path(self):
        self.assertEqual(
            clean_photo_url("scans/2026/07/file.jpg"),
            "https://res.cloudinary.com/demo/scans/2026/07/file.jpg",
        )
