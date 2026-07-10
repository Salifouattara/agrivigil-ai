from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase, override_settings

from core.expert_engine import (
    _build_prompt,
    _reply_simulated,
    generate_expert_reply,
)


class FakeExpert:
    id = "plant_issouf"
    name = "Dr. Issouf Touré"
    role = "Médecin de plantes"
    specialty = "Phytopathologie"
    location = "Abidjan"


class ExpertEngineTests(SimpleTestCase):
    def test_build_prompt_includes_persona_and_history(self):
        history = [
            {"sender_role": "farmer", "sender_name": "Agriculteur", "content": "Première question"},
            {"sender_role": "expert", "sender_name": "Dr. Issouf Touré", "content": "Première réponse"},
        ]
        prompt = _build_prompt(FakeExpert(), "Question de suivi", history)

        self.assertIn("Dr. Issouf Touré", prompt)
        self.assertIn("Phytopathologie", prompt)
        self.assertIn("Première question", prompt)
        self.assertIn("Question de suivi", prompt)

    @override_settings(GEMINI_API_KEY="")
    def test_generate_expert_reply_uses_simulated_without_api_key(self):
        reply = generate_expert_reply(FakeExpert(), "Mes feuilles jaunissent")
        self.assertIn("Mes feuilles jaunissent", reply)

    @override_settings(GEMINI_API_KEY="test-key")
    @patch("core.expert_engine._reply_with_gemini")
    def test_generate_expert_reply_calls_gemini_when_key_set(self, mock_gemini):
        mock_gemini.return_value = "Réponse IA contextualisée."
        expert = FakeExpert()
        history = [{"sender_role": "farmer", "content": "Bonjour"}]

        reply = generate_expert_reply(expert, "Question", history)

        mock_gemini.assert_called_once()
        args, _kwargs = mock_gemini.call_args
        self.assertEqual(args[0], expert)
        self.assertEqual(args[1], "Question")
        self.assertEqual(args[2], history)
        self.assertEqual(reply, "Réponse IA contextualisée.")

    @override_settings(GEMINI_API_KEY="test-key")
    @patch("google.genai.Client")
    def test_reply_with_gemini_propagates_errors(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = RuntimeError("API down")
        mock_client_cls.return_value = mock_client

        from core.expert_engine import _reply_with_gemini

        with self.assertRaises(RuntimeError):
            _reply_with_gemini(FakeExpert(), "Question", [])

    def test_reply_simulated_returns_french_template(self):
        reply = _reply_simulated(FakeExpert(), "Problème de cacao")
        self.assertIn("Problème de cacao", reply)
