"""
Conseils agronomiques par culture — pesticides homologués, bonnes pratiques.

Base de connaissances statique pour le MVP, enrichie par Gemini si disponible.
"""

import json
import logging

from django.conf import settings

logger = logging.getLogger(__name__)

MODEL_NAME = "gemini-2.5-flash"

CROP_ADVICE_DATA = {
    "cacao": {
        "crop_label": "Cacao",
        "season_tips": [
            "Récolter les cabosses mûres toutes les 2 semaines en saison.",
            "Élaguer les branches basse ombre pour aérer la cacaoyère.",
            "Appliquer la bouillie bordelaise en début de saison des pluies.",
        ],
        "best_practices": [
            "Maintenir un ombrage à 30-40% pour protéger les cacaoyers jeunes.",
            "Pailler le pied des cacaoyers pour conserver l'humidité.",
            "Rotation des produits phytosanitaires pour éviter les résistances.",
            "Détruire les cabosses pourries pour limiter la pourriture brune.",
        ],
        "approved_pesticides": [
            {"name": "Bouillie bordelaise", "target": "Phytophthora, maladies fongiques", "note": "Homologué cacao, préventif"},
            {"name": "Confidor / Imidaclopride", "target": "Mirides, punaises", "note": "Respecter la période de retrait avant récolte"},
            {"name": "Actara (Thiamethoxam)", "target": "Mirides", "note": "Application ciblée sur rameaux"},
        ],
        "common_issues": ["Pourriture brune", "Mirides", "Swollen shoot (CSSV)"],
    },
    "café": {
        "crop_label": "Café",
        "season_tips": [
            "Tailler après la récolte pour stimuler la nouvelle croissance.",
            "Renforcer la fertilisation potassique avant la floraison.",
            "Surveiller la rouille orangée dès les premières pluies.",
        ],
        "best_practices": [
            "Densité recommandée : 5000-6000 pieds/ha selon variété.",
            "Association café + bananier plantain pour l'ombrage.",
            "Récolter uniquement les cerises rouges mûres.",
            "Composter les pulpes de cerise pour enrichir le sol.",
        ],
        "approved_pesticides": [
            {"name": "Oxychlorure de cuivre", "target": "Rouille orangée", "note": "Traitement préventif en saison humide"},
            {"name": "Cymoxanil + Mancozebe", "target": "Maladies fongiques", "note": "Alterner les modes d'action"},
        ],
        "common_issues": ["Rouille orangée", "Nématodes", "Carence en potassium"],
    },
    "manioc": {
        "crop_label": "Manioc",
        "season_tips": [
            "Planter en début de saison des pluies avec boutures saines.",
            "Buttage à 6-8 semaines pour favoriser le tubercule.",
            "Récolter entre 9 et 18 mois selon la variété.",
        ],
        "best_practices": [
            "Utiliser exclusivement des boutures certifiées sans mosaïque.",
            "Rotation obligatoire : ne pas replanter manioc sur la même parcelle avant 3 ans.",
            "Désherbage manuel les 3 premiers mois.",
            "Éviter les sols mal drainés.",
        ],
        "approved_pesticides": [
            {"name": "Diméthoate", "target": "Mouche blanche (vecteur mosaïque)", "note": "Lutte intégrée prioritaire"},
            {"name": "Bouillie cuprique", "target": "Bactériose", "note": "Préventif en période humide"},
        ],
        "common_issues": ["Mosaïque africaine", "Bactériose", "Acariens"],
    },
    "riz": {
        "crop_label": "Riz",
        "season_tips": [
            "Repiquer les plants à 20-25 cm en lignes espacées de 20 cm.",
            "Maintenir 5-10 cm d'eau en phase végétative.",
            "Drainer 2 semaines avant la récolte.",
        ],
        "best_practices": [
            "Utiliser des semences certifiées à haut rendement (Nerica, WAB).",
            "Fertilisation fractionnée : 1/3 à repiquage, 2/3 en couvert.",
            "Rotation riz / légumineuses pour restaurer l'azote.",
            "Nivellement soigné pour une gestion uniforme de l'eau.",
        ],
        "approved_pesticides": [
            {"name": "Tricyclazole", "target": "Pyriculariose", "note": "Dès les premières taches foliaires"},
            {"name": "Cartap hydrochloride", "target": "Pyrale, foreurs", "note": "Respecter les doses homologuées"},
        ],
        "common_issues": ["Pyriculariose", "Pyrale du riz", "Oiseaux granivores"],
    },
    "maïs": {
        "crop_label": "Maïs",
        "season_tips": [
            "Semer dès le début des pluies à 75 cm x 25 cm.",
            "Premier désherbage à 3 semaines, second à 6 semaines.",
            "Récolter quand l'humidité des grains est ~20%.",
        ],
        "best_practices": [
            "Densité : 50 000-60 000 plants/ha selon variété.",
            "Apport d'azote en 2 temps (semis + 6 semaines).",
            "Rotation avec légumineuses ou céréales.",
            "Stockage hermétique (PICS bags) contre les insectes.",
        ],
        "approved_pesticides": [
            {"name": "Mancozèbe", "target": "Rouille, Helminthosporiose", "note": "Préventif foliaire"},
            {"name": "Lambda-cyhalothrine", "target": "Foreurs, chenilles", "note": "Traitement curatif ciblé"},
        ],
        "common_issues": ["Rouille", "Striga", "Foreur de tige"],
    },
    "igname": {
        "crop_label": "Igname",
        "season_tips": [
            "Planter les semenceaux sur buttes ou billons bien drainés.",
            "Tuteurage obligatoire pour les variétés à gros tubercules.",
            "Récolter 7-10 mois après plantation.",
        ],
        "best_practices": [
            "Associer igname + maïs ou légumes pour optimiser l'espace.",
            "Buttage régulier pour favoriser le grossissement.",
            "Rotation des cultures sur 3 ans minimum.",
            "Conserver les semenceaux dans un endroit sec et ventilé.",
        ],
        "approved_pesticides": [
            {"name": "Bouillie bordelaise", "target": "Anthracnose", "note": "Préventif en saison des pluies"},
            {"name": "Abamectine", "target": "Nématodes foliaires", "note": "Selon avis technique local"},
        ],
        "common_issues": ["Anthracnose", "Nématodes", "Gale de l'igname"],
    },
    "banane_plantain": {
        "crop_label": "Banane plantain",
        "season_tips": [
            "Planter en poquet de 3-5 rejets espacés de 3 m x 3 m.",
            "Supprimer les rejets excédentaires pour concentrer la production.",
            "Récolter quand les doigts sont pleins et les arêtes arrondies.",
        ],
        "best_practices": [
            "Pailler abondamment autour du pied.",
            "Apporter compost et NPK régulièrement (forte demande en K).",
            "Protéger les régimes avec un sac après émergence.",
            "Détruire les souches après récolte (maladies du collet).",
        ],
        "approved_pesticides": [
            {"name": "Mancozebe + systémique", "target": "Cercosporiose (raies noires)", "note": "Effeuillage sanitaire + traitement"},
            {"name": "Imidaclopride", "target": "Pucerons, thrips", "note": "Application localisée"},
        ],
        "common_issues": ["Cercosporiose", "Charançons", "Nématodes"],
    },
    "hévéa": {
        "crop_label": "Hévéa",
        "season_tips": [
            "Ouverture des saignées après 6 ans de plantation.",
            "Saignée en demi-spirale, alterner les côtés.",
            "Suspendre la saignée en saison sèche si écoulement faible.",
        ],
        "best_practices": [
            "Densité : 500-550 pieds/ha en plantation pure.",
            "Couverture du sol par légumineuses (Pueraria).",
            "Fertilisation NPK annuelle adaptée à l'âge du verger.",
            "Surveillance de la maladie des feuilles en période humide.",
        ],
        "approved_pesticides": [
            {"name": "Fongicides cupriques", "target": "Maladie des feuilles (Microcyclus)", "note": "Préventif en refoliation"},
            {"name": "Glyphosate (bordure)", "target": "Adventices", "note": "Éviter contact avec l'écorce"},
        ],
        "common_issues": ["Maladie des feuilles", "Tigre du caoutchouc", "Ecorces sèches"],
    },
    "palmier_huile": {
        "crop_label": "Palmier à huile",
        "season_tips": [
            "Récolter les régimes mûres (3-5 kg) toutes les 10-14 jours.",
            "Entretenir le couvert végétal entre les rangs.",
            "Surveiller la fusariose (dessèchement en éventail).",
        ],
        "best_practices": [
            "Densité : 143-160 pieds/ha (triangles 9 m).",
            "Fertilisation NPK + Mg adaptée à l'âge (croissance vs production).",
            "Arrachage immédiat des palmiers atteints de fusariose.",
            "Utiliser des semences certifiées D x P.",
        ],
        "approved_pesticides": [
            {"name": "Fongicides systémiques", "target": "Ganoderma, maladies du collet", "note": "Prévention par bon drainage"},
            {"name": "Bacillus thuringiensis", "target": "Chenilles défoliatrices", "note": "Lutte biologique privilégiée"},
        ],
        "common_issues": ["Fusariose", "Ganoderma", "Acariens du palmier"],
    },
    "coton": {
        "crop_label": "Coton",
        "season_tips": [
            "Semis en début de saison des pluies, densité 40 000-50 000 plants/ha.",
            "Sarclage et buttage aux stades clés.",
            "Récolte manuelle quand 80% des capsules sont ouvertes.",
        ],
        "best_practices": [
            "Rotation coton / céréales / légumineuses obligatoire.",
            "Lutte intégrée contre le ver de capsule (pièges phéromones).",
            "Fertilisation NPK selon analyse de sol.",
            "Stockage des capsules dans un local sec et ventilé.",
        ],
        "approved_pesticides": [
            {"name": "Deltamethrine", "target": "Ver de capsule (Heliothis)", "note": "Seuil de traitement : 5 chenilles/100 capsules"},
            {"name": "Endosulfan (selon réglementation)", "target": "Punaises", "note": "Vérifier homologation en vigueur"},
        ],
        "common_issues": ["Ver de capsule", "Punaises vertes", "Fusariose"],
    },
}


def get_crop_advice(crop_type: str) -> dict:
    """Retourne les conseils statiques pour une culture."""
    data = CROP_ADVICE_DATA.get(crop_type)
    if not data:
        raise ValueError(f"Culture inconnue: {crop_type}")
    return {
        "crop_type": crop_type,
        "crop_label": data["crop_label"],
        "season_tips": data["season_tips"],
        "best_practices": data["best_practices"],
        "approved_pesticides": data["approved_pesticides"],
        "common_issues": data["common_issues"],
        "ai_enriched": False,
    }


def _enrich_with_gemini(crop_type: str, base_advice: dict) -> dict:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    prompt = (
        f"Tu es un agronome conseiller pour les agriculteurs ivoiriens. "
        f"Enrichis les conseils pour la culture {base_advice['crop_label']} ({crop_type}). "
        f"Conseils existants : {json.dumps(base_advice, ensure_ascii=False)}. "
        f"Ajoute 2 conseils saisonniers supplémentaires pertinents pour la Côte d'Ivoire, "
        f"1 bonne pratique supplémentaire, et un paragraphe 'additional_notes' (3 phrases max) "
        f"sur les pesticides homologués et la sécurité. Réponds en JSON avec les clés : "
        f"season_tips (liste), best_practices (liste), additional_notes (string)."
    )

    schema = {
        "type": "object",
        "properties": {
            "season_tips": {"type": "array", "items": {"type": "string"}},
            "best_practices": {"type": "array", "items": {"type": "string"}},
            "additional_notes": {"type": "string"},
        },
        "required": ["season_tips", "best_practices", "additional_notes"],
    }

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema,
            temperature=0.3,
        ),
    )

    enriched = json.loads(response.text)
    result = {**base_advice}
    result["season_tips"] = base_advice["season_tips"] + enriched.get("season_tips", [])[:2]
    result["best_practices"] = base_advice["best_practices"] + enriched.get("best_practices", [])[:1]
    result["additional_notes"] = enriched.get("additional_notes", "")
    result["ai_enriched"] = True
    return result


def get_crop_advice_enriched(crop_type: str) -> dict:
    base = get_crop_advice(crop_type)
    if settings.GEMINI_API_KEY:
        try:
            return _enrich_with_gemini(crop_type, base)
        except Exception as exc:
            logger.warning("Enrichissement IA conseils échoué pour %s : %s", crop_type, exc)
    return base
