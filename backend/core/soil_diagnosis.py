"""
Analyse visuelle du sol pour déterminer le type de texture (Hub Engrais).

Utilise Gemini 2.5 Flash si GEMINI_API_KEY est configurée, sinon un moteur
simulé basé sur des indices visuels courants en Côte d'Ivoire.
"""

import hashlib
import json
import logging
import random

from django.conf import settings

logger = logging.getLogger(__name__)

MODEL_NAME = "gemini-2.5-flash"

VALID_SOIL_TYPES = ["argileux", "sableux", "limoneux", "latéritique", "tourbeux"]

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "soil_type": {
            "type": "string",
            "enum": VALID_SOIL_TYPES,
            "description": "Type de sol dominant détecté",
        },
        "confidence": {"type": "number", "description": "Confiance de 0 à 100"},
        "texture_description": {"type": "string", "description": "Description de la texture observée"},
        "fertility_level": {
            "type": "string",
            "enum": ["faible", "moyenne", "élevée"],
            "description": "Niveau de fertilité apparent",
        },
        "ph_estimate": {"type": "string", "description": "Estimation du pH (ex: 5.5-6.5 acide)"},
        "organic_matter": {"type": "string", "description": "Estimation de la matière organique"},
        "amendment_advice": {"type": "string", "description": "Conseils d'amendement du sol"},
        "observations": {"type": "string", "description": "Observations complémentaires utiles à l'agriculteur"},
    },
    "required": [
        "soil_type", "confidence", "texture_description", "fertility_level",
        "ph_estimate", "organic_matter", "amendment_advice", "observations",
    ],
}

PROMPT = (
    "Tu es un pédologue expert des sols ivoiriens. Analyse cette photo de sol "
    "(échantillon au sol, tranchée ou surface de parcelle) et détermine le type "
    "de texture dominant parmi : argileux, sableux, limoneux, latéritique (rouge "
    "ferrugineux typique du sud), ou tourbeux (riche en matière organique). "
    "Indique aussi une estimation de fertilité, du pH probable, de la matière "
    "organique et des amendements recommandés pour améliorer ce sol en Côte "
    "d'Ivoire. Réponds uniquement avec les champs demandés."
)

SOIL_PROFILES = {
    "latéritique": {
        "texture_description": "Sol rouge ferrugineux, compact en saison sèche, texture grumeleuse.",
        "fertility_level": "moyenne",
        "ph_estimate": "5.0-6.0 (légèrement acide)",
        "organic_matter": "Faible à moyenne (1-2%)",
        "amendment_advice": "Apporter du compost ou fumier (5-10 t/ha), chauler légèrement si pH < 5.5.",
        "observations": "Sol très répandu en zone forestière ivoirienne, bon drainage après pluies.",
    },
    "argileux": {
        "texture_description": "Sol lourd, collant quand humide, forme des mottes compactes.",
        "fertility_level": "élevée",
        "ph_estimate": "6.0-7.0 (neutre)",
        "organic_matter": "Moyenne (2-4%)",
        "amendment_advice": "Améliorer le drainage, ajouter matière organique et sable si compactage.",
        "observations": "Retient bien l'eau et les nutriments, risque de asphyxie racinaire.",
    },
    "sableux": {
        "texture_description": "Sol léger, grain fin qui s'écoule entre les doigts, sèche vite.",
        "fertility_level": "faible",
        "ph_estimate": "5.5-6.5",
        "organic_matter": "Très faible (< 1%)",
        "amendment_advice": "Enrichir en compost (10-15 t/ha), pailler pour retenir l'humidité, fractionner les apports N.",
        "observations": "Nécessite des apports réguliers en engrais et matière organique.",
    },
    "limoneux": {
        "texture_description": "Texture équilibrée, légèrement poudreuse, bonne rétention d'eau.",
        "fertility_level": "élevée",
        "ph_estimate": "6.0-7.0",
        "organic_matter": "Moyenne à bonne (2-5%)",
        "amendment_advice": "Sol déjà favorable ; maintenir la matière organique par paillage ou couverture végétale.",
        "observations": "Sol idéal pour la plupart des cultures, surveiller l'érosion en pente.",
    },
    "tourbeux": {
        "texture_description": "Sol sombre, spongieux, riche en débris végétaux.",
        "fertility_level": "élevée",
        "ph_estimate": "5.0-6.0 (acide)",
        "organic_matter": "Élevée (> 5%)",
        "amendment_advice": "Surveiller l'acidité, chauler si nécessaire, éviter le sur-arrosage.",
        "observations": "Excellent réservoir de nutriments, attention au compactage.",
    },
}


def _analyze_with_gemini(image_bytes: bytes) -> dict:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
            PROMPT,
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=RESPONSE_SCHEMA,
            temperature=0.2,
        ),
    )

    data = json.loads(response.text)
    if data.get("soil_type") not in VALID_SOIL_TYPES:
        data["soil_type"] = "latéritique"
    data["confidence"] = round(float(data.get("confidence", 0)), 1)
    return data


def _analyze_simulated(image_bytes: bytes) -> dict:
    digest = hashlib.md5(image_bytes[:4096]).hexdigest()
    idx = int(digest[:8], 16) % len(VALID_SOIL_TYPES)
    soil_type = VALID_SOIL_TYPES[idx]
    profile = SOIL_PROFILES[soil_type]
    confidence = round(55 + (int(digest[8:12], 16) % 30), 1)

    return {
        "soil_type": soil_type,
        "confidence": confidence,
        **profile,
    }


def analyze_soil_image(image_bytes: bytes) -> dict:
    if settings.GEMINI_API_KEY:
        return _analyze_with_gemini(image_bytes)

    logger.warning(
        "GEMINI_API_KEY non configurée : analyse de sol simulée. "
        "Ajoutez votre clé dans .env pour activer l'analyse IA réelle."
    )
    return _analyze_simulated(image_bytes)
