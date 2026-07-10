from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import CropScan, CropScanTracking

User = get_user_model()


class TrackingAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="farmer@agrivigil.ci",
            password="securepassword123",
            full_name="Jean Konan"
        )
        self.client.force_authenticate(user=self.user)
        
        # Création d'un suivi de test
        self.tracking = CropScanTracking.objects.create(
            owner=self.user,
            name="Manioc Parcelle A",
            status="active"
        )

    def test_list_trackings(self):
        url = reverse("tracking-list-create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Manioc Parcelle A")

    def test_create_tracking(self):
        url = reverse("tracking-list-create")
        data = {"name": "Poule Poulailler B"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CropScanTracking.objects.filter(owner=self.user).count(), 2)
        self.assertEqual(response.data["name"], "Poule Poulailler B")

    def test_delete_tracking_leaves_scans_intact(self):
        # Créer un scan lié
        import tempfile
        from django.core.files.uploadedfile import SimpleUploadedFile
        from PIL import Image

        image = Image.new("RGB", (100, 100))
        tmp_file = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        image.save(tmp_file.name)
        tmp_file.seek(0)
        
        uploaded_image = SimpleUploadedFile(
            name="test_crop.jpg",
            content=tmp_file.read(),
            content_type="image/jpeg"
        )

        scan = CropScan.objects.create(
            owner=self.user,
            image=uploaded_image,
            crop_name="Manioc",
            disease_name="Mosaïque",
            severity="élevée",
            tracking=self.tracking
        )

        # Vérifier liaison
        self.assertEqual(scan.tracking, self.tracking)

        # Supprimer le suivi
        url = reverse("tracking-detail", kwargs={"pk": self.tracking.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Le suivi doit être supprimé
        self.assertFalse(CropScanTracking.objects.filter(id=self.tracking.id).exists())

        # Le scan doit toujours exister mais avec tracking = None
        scan.refresh_from_db()
        self.assertIsNone(scan.tracking)
        self.assertEqual(scan.crop_name, "Manioc")
