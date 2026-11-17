"""Reponses IA des assistants agronomiques via Gemini, sans repli vers des reponses aleatoires."""

import logging
import random

from django.conf import settings
from .ai_service import create_gemini_client

logger = logging.getLogger(__name__)

MODEL_NAME = "gemini-2.5-flash"
MAX_HISTORY_MESSAGES = 10

GENERIC_OPENERS = [
    "Merci pour votre message.",
    "Je comprends votre préoccupation.",
    "Bonne question.",
    "D'après ce que vous décrivez,",
]

PLANT_ADVICE = [
    "il serait utile d'envoyer une photo via le Scan IA pour un diagnostic plus précis.",
    "pensez à vérifier l'humidité du sol et l'aération de la parcelle avant tout traitement.",
    "un traitement préventif à base de cuivre peut limiter la propagation si c'est fongique.",
    "surveillez l'évolution sur 2-3 jours et évitez tout excès d'arrosage en attendant.",
]

VET_ADVICE = [
    "isolez l'animal concerné des autres pour éviter toute propagation.",
    "vérifiez la température et l'appétit de l'animal dans les prochaines 24h.",
    "assurez un accès permanent à l'eau propre et à l'ombre.",
    "contactez un poste vétérinaire local si les symptômes persistent plus de 48h.",
]

CHATBOT_ADVICE = [
    "essaye de préciser le symptôme ou la culture pour que je t'aide mieux.",
    "si tu peux, envoie une photo via le Scan IA pour un diagnostic plus précis.",
    "je peux te guider sur l'humidité du sol, les ravageurs ou la santé de ton élevage.",
    "surveille l'évolution dans les prochaines 24h et évite les traitements trop agressifs sans avis.",
]


def _format_history(history: list[dict]) -> str:
    if not history:
        return ""
    lines = []
    for msg in history[-MAX_HISTORY_MESSAGES:]:
        role_label = "Agriculteur" if msg.get("sender_role") == "farmer" else msg.get("sender_name", "Expert")
        lines.append(f"{role_label}: {msg.get('content', '').strip()}")
    return "Historique de la conversation:\n" + "\n".join(lines) + "\n\n"


def _build_prompt(expert, question: str, history: list[dict]) -> str:
    history_block = _format_history(history)
    return (
        f"Tu es {expert.name}, {expert.role} spécialiste en {expert.specialty}, "
        f"basé à {expert.location}. "
        f"{history_block}"
        f"Un agriculteur ivoirien te pose cette question: \"{question.strip()}\". "
        f"Réponds de façon concise, pratique et bienveillante, en français, "
        f"comme un vrai {expert.role} conseillerait un agriculteur. "
        f"Limite ta réponse à 3-4 phrases."
    )


def _reply_with_gemini(expert, question: str, history: list[dict]) -> str:
    from google import genai
    from google.genai import types

    client = create_gemini_client()
    prompt = _build_prompt(expert, question, history)

    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents=[prompt],
        config=types.GenerateContentConfig(temperature=0.4),
    )

    text = (response.text or "").strip()
    if not text:
        raise ValueError("Gemini a renvoyé une réponse vide.")
    return text


def _reply_simulated(expert, question: str) -> str:
    opener = random.choice(GENERIC_OPENERS)
    if expert.role == "Médecin de plantes":
        advice_pool = PLANT_ADVICE
    elif expert.role == "Vétérinaire":
        advice_pool = VET_ADVICE
    else:
        advice_pool = CHATBOT_ADVICE
    advice = random.choice(advice_pool)
    return (
        f"{opener} Concernant « {question.strip()[:80]} », {advice} "
        f"N'hésitez pas à me tenir informé(e) de l'évolution."
    )


def _is_quota_error(exception: Exception) -> bool:
    text = str(exception).upper()
    return "RESOURCE_EXHAUSTED" in text or "QUOTA" in text or "429" in text


def _reply_quota_exhausted() -> str:
    return (
        "Je suis désolé(e), vous n'avez actuellement plus de quota disponible. "
        "Je ne peux pas répondre pour l'instant. Réessaie plus tard."
    )


class ChatbotPersona:
    name = "Agrivigil IA"
    role = "Assistant virtuel"
    specialty = "Conseils agronomiques et vétérinaires"
    location = "Disponible en continu"


def generate_chatbot_reply(question: str, history: list[dict] | None = None) -> str:
    return _reply_with_gemini(ChatbotPersona(), question, history or [])


def generate_expert_reply(expert, question: str, history: list[dict] | None = None) -> str:
    return _reply_with_gemini(expert, question, history or [])
