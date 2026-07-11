from unittest.mock import patch

from django.test import SimpleTestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.utils import TTSServiceError, synthesize_text_to_speech


class TTSUtilityTests(SimpleTestCase):
    @patch("core.utils.default_storage")
    @patch("core.utils._load_tts_pipeline")
    @patch("core.utils._write_wav_file")
    def test_synthesize_text_to_speech_returns_storage_url(self, mock_write_wav, mock_load_pipeline, mock_storage):
        mock_storage.save.return_value = "tts/demo.wav"
        mock_storage.url.return_value = "/media/tts/demo.wav"
        tokenizer = lambda *_args, **_kwargs: {"input_ids": [1]}
        model = lambda **_kwargs: type("Output", (), {"waveform": [type("Audio", (), {"detach": lambda self: self})()]})()
        mock_load_pipeline.return_value = (model, tokenizer)
        mock_write_wav.return_value = None

        with patch("core.utils.torch") as mock_torch:
            mock_torch.no_grad.return_value.__enter__.return_value = None
            mock_torch.no_grad.return_value.__exit__.return_value = None

            result = synthesize_text_to_speech(
                "Bonjour, ceci est un test de synthèse vocale.",
                token="demo-token",
                model_name="demo/model",
                save_to_storage=True,
            )

        self.assertEqual(result["audio_url"], "/media/tts/demo.wav")
        mock_storage.save.assert_called_once()


class DioulaSynthesisViewTests(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()

    @patch("core.views.synthesize_text_to_speech")
    def test_synthesize_dioula_returns_audio_url(self, mock_synthesize):
        mock_synthesize.return_value = {"audio_url": "/media/tts/demo.mp3", "path": "tts/demo.mp3"}

        response = self.client.post(reverse("synthesize-dioula"), {"text": "Bonjour Dioula"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["audio_url"], "/media/tts/demo.mp3")

    @patch("core.views.synthesize_text_to_speech")
    def test_synthesize_dioula_returns_error_when_tts_fails(self, mock_synthesize):
        mock_synthesize.side_effect = TTSServiceError("Le modèle est indisponible")

        response = self.client.post(reverse("synthesize-dioula"), {"text": "Bonjour Dioula"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertIn("indisponible", response.json()["detail"])
