from datetime import date
from io import BytesIO
from unittest.mock import Mock, patch

from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, override_settings
from PIL import Image
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory

from core.ai_diagnosis import diagnose_crop_image
from core.ai_service import AIUnavailableError, read_uploaded_image
from core.models import CropScan
from core.serializers import CropScanSerializer
from core.soil_diagnosis import analyze_soil_image
from core.weather import WeatherAPIError, get_weather


class LocalReadinessTests(SimpleTestCase):
    @override_settings(GEMINI_API_KEY='')
    def test_missing_ai_key_never_creates_a_simulated_diagnosis(self):
        for analyze in (diagnose_crop_image, analyze_soil_image):
            with self.assertRaises(AIUnavailableError):
                analyze(b'not-an-image')

    def test_invalid_upload_is_rejected_before_calling_provider(self):
        upload = SimpleUploadedFile('plant.jpg', b'not-an-image')
        with self.assertRaises(ValidationError):
            read_uploaded_image(upload)

    def test_valid_png_is_accepted_and_file_is_rewound(self):
        stream = BytesIO()
        Image.new('RGB', (5, 5)).save(stream, format='PNG')
        upload = SimpleUploadedFile('plant.png', stream.getvalue())
        self.assertEqual(read_uploaded_image(upload), stream.getvalue())
        self.assertEqual(upload.tell(), 0)

    @override_settings(MEDIA_URL='/media/', ALLOWED_HOSTS=['testserver'], STORAGES={'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'}})
    def test_local_scan_photo_keeps_its_url_and_webp_extension(self):
        request = APIRequestFactory().get('/')
        scan = CropScan(image='scans/plant.webp')
        data = CropScanSerializer(scan, context={'request': request}).data
        self.assertEqual(data['image_url'], 'http://testserver/media/scans/plant.webp')

    @override_settings(OPENWEATHER_API_KEY='test')
    @patch('core.weather.requests.get')
    def test_weather_uses_real_forecast_rain_probability_and_caches(self, mocked_get):
        cache.clear()
        current = {'dt': 1794916800, 'main': {'temp': 30, 'humidity': 80}, 'weather': [{'main': 'Clouds'}]}
        entries = [{'dt_txt': f'2026-11-{day} 12:00:00', 'main': {'temp': 29}, 'pop': 0.8, 'weather': [{'main': 'Rain'}]} for day in range(17, 21)]
        mocked_get.side_effect = [Mock(status_code=200, json=lambda: current), Mock(status_code=200, json=lambda: {'list': entries})]
        data = get_weather('Abidjan', date(2026, 11, 17))
        self.assertEqual(data['rain_probability'], 80)
        self.assertEqual(len(data['forecast_3days']), 3)
        self.assertEqual(get_weather('Abidjan', date(2026, 11, 17)), data)
        self.assertEqual(mocked_get.call_count, 2)

    @override_settings(OPENWEATHER_API_KEY='test')
    @patch('core.weather.requests.get')
    def test_weather_network_error_has_a_safe_message(self, mocked_get):
        import requests
        cache.clear()
        mocked_get.side_effect = requests.Timeout('secret-in-provider-url')
        with self.assertRaises(WeatherAPIError) as caught:
            get_weather('Abidjan')
        self.assertNotIn('secret-in-provider-url', str(caught.exception))
