"""
Moteur de diagnostic pour le Scan IA — appelle réellement Gemini pour
analyser l'image de culture envoyée par l'agriculteur.

Note sur le modèle : le projet visait initialement "Gemini 1.5 Flash", mais
ce modèle (ainsi que toute la génération 1.5) a été définitivement arrêté par
Google mi-2026 — tout appel vers lui renvoie une erreur 404. Ce module utilise
donc **Gemini 2.5 Flash** (gemini-2.5-flash), le modèle Flash stable et
disponible en production au moment de l'écriture, avec support multimodal
(texte + image) et sortie JSON structurée. Si Google publie une version plus
récente, il suffit de changer la constante MODEL_NAME ci-dessous.

Si aucune clé GEMINI_API_KEY n'est configurée (ex: développement local sans
compte Google AI Studio), le module bascule sur un moteur simulé basé sur une
vraie base de maladies ivoiriennes, pour ne jamais bloquer le développement.
Dès qu'une clé est présente, c'est TOUJOURS le vrai modèle qui est appelé —
aucun repli silencieux en cas d'erreur réseau, pour que les problèmes soient
visibles plutôt que masqués.
"""

import hashlib
import json
import logging
import random

from django.conf import settings

logger = logging.getLogger(__name__)

MODEL_NAME = "gemini-2.5-flash"

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "crop_name": {"type": "string", "description": "Nom de la culture identifiée (ex: cacao, manioc, riz...)"},
        "is_healthy": {"type": "boolean", "description": "La plante semble-t-elle saine ?"},
        "disease_name": {"type": "string", "description": "Nom de la maladie détectée, chaîne vide si saine"},
        "severity": {"type": "string", "enum": ["faible", "modérée", "élevée", "critique"]},
        "symptoms": {"type": "string", "description": "Symptômes observés sur l'image"},
        "remedy": {"type": "string", "description": "Remède recommandé, concret et actionnable"},
        "dosage": {"type": "string", "description": "Dosage précis du traitement, avec unités"},
        "prevention": {"type": "string", "description": "Conseils de prévention pour éviter la récidive"},
        "confidence": {"type": "number", "description": "Score de confiance du diagnostic, de 0 à 100"},
        "is_valid_subject": {"type": "boolean", "description": "Est-ce une plante ou un animal d'élevage valide ? (false si ce n'est pas une plante/animal ou si non-identifié)"},
    },
    "required": [
        "crop_name", "is_healthy", "disease_name", "severity",
        "symptoms", "remedy", "dosage", "prevention", "confidence", "is_valid_subject",
    ],
}

PROMPT = (
    "Tu es un spécialiste vétérinaire et agronome pour les exploitations ivoiriennes. "
    "Tu peux diagnostiquer des plantes (cacao, café, manioc, riz, maïs, igname, banane plantain, hévéa, palmier à huile, coton) "
    "ou des animaux d'élevage (bovins, ovins, volailles). "
    "⚠️ IMPORTANT: Si l'image n'est PAS une plante ou un animal d'élevage valide, réponds TOUJOURS avec is_valid_subject=false et les autres champs vides/valeur par défaut. "
    "Analyse attentivement cette photo et fournis un diagnostic précis et pratique, utile à quelqu'un sur le terrain. "
    "Si c'est bien une plante ou un animal valide: Si l'animal ou la plante paraît sain(e), dis-le clairement. Si tu détectes une maladie, une carence ou un ravageur, "
    "identifie-le aussi précisément que possible, indique sa gravité, un remède concret disponible en Côte d'Ivoire, "
    "un dosage précis si applicable, et des conseils de prévention. Réponds uniquement avec les champs demandés."
)


def _diagnose_with_gemini(image_bytes: bytes, declared_crop: str | None) -> dict:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=settings.GEMINI_API_KEY)

    prompt = PROMPT
    if declared_crop:
        prompt += f" L'agriculteur indique qu'il s'agit de : {declared_crop}."

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
            prompt,
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=RESPONSE_SCHEMA,
            temperature=0.2,
        ),
    )

    data = json.loads(response.text)
    # Garde-fous : normalise les types au cas où le modèle dévie légèrement.
    data["confidence"] = round(float(data.get("confidence", 0)), 1)
    data["is_healthy"] = bool(data.get("is_healthy", False))
    return data


def diagnose_crop_image(image_bytes: bytes, declared_crop: str | None = None) -> dict:
    """
    Diagnostique une image de culture.

    Utilise Gemini 2.5 Flash si `settings.GEMINI_API_KEY` est configurée.
    Sinon, bascule sur le moteur simulé (voir `_diagnose_simulated`) — utile
    uniquement pour développer sans clé API, jamais utilisé silencieusement
    en production si une clé est présente.
    """
    if settings.GEMINI_API_KEY:
        return _diagnose_with_gemini(image_bytes, declared_crop)

    logger.warning(
        "GEMINI_API_KEY non configurée : utilisation du moteur de diagnostic simulé. "
        "Ajoutez votre clé dans le fichier .env pour activer le vrai diagnostic IA."
    )
    return _diagnose_simulated(image_bytes, declared_crop)

# Base de connaissances agronomiques : maladies réelles des cultures
# ivoiriennes les plus courantes, avec remèdes et dosages usuels.
DISEASE_DATABASE = {
    "cacao": [
        {
            "disease_name": "Pourriture brune des cabosses (Phytophthora)",
            "severity": "élevée",
            "symptoms": "Taches brunes qui s'étendent rapidement sur la cabosse, "
                        "surface qui devient noire et se couvre parfois d'un duvet blanchâtre.",
            "remedy": "Retirer et détruire immédiatement les cabosses atteintes. "
                      "Traiter au fongicide cuprique (bouillie bordelaise) en début de saison des pluies.",
            "dosage": "Bouillie bordelaise à 0,5% : 2,5 kg pour 500 L d'eau/ha, "
                      "en 3 applications espacées de 3 semaines.",
            "prevention": "Élaguer pour aérer la cacaoyère, éviter l'excès d'humidité au sol, "
                          "récolter régulièrement les cabosses mûres.",
        },
        {
            "disease_name": "Mirides (punaises du cacaoyer)",
            "severity": "modérée",
            "symptoms": "Petites taches noires sur les branches et cabosses, "
                        "dessèchement progressif des rameaux piqués.",
            "remedy": "Traitement insecticide ciblé en début et fin de saison des pluies, "
                      "période de forte activité des mirides.",
            "dosage": "Insecticide homologué cacao : suivre la dose du fabricant, "
                      "généralement 1 L/ha en pulvérisation dirigée.",
            "prevention": "Maintenir une ombre légère, éviter la surdensité de plantation.",
        },
    ],
    "café": [
        {
            "disease_name": "Rouille orangée du caféier (Hemileia vastatrix)",
            "severity": "élevée",
            "symptoms": "Poudre orangée sous les feuilles, jaunissement puis chute prématurée du feuillage.",
            "remedy": "Fongicide à base de cuivre dès les premiers symptômes, "
                      "renforcer la fertilisation potassique pour la résistance de la plante.",
            "dosage": "Oxychlorure de cuivre à 0,3% : 1,5 kg/ha, répéter tous les 21 jours en saison des pluies.",
            "prevention": "Tailler pour aérer les caféiers, éviter l'ombrage excessif.",
        },
    ],
    "manioc": [
        {
            "disease_name": "Mosaïque africaine du manioc",
            "severity": "critique",
            "symptoms": "Feuilles mosaïquées (mélange de vert clair et foncé), déformées et réduites.",
            "remedy": "Arracher et détruire les plants atteints. Utiliser exclusivement des boutures saines "
                      "certifiées pour la prochaine plantation.",
            "dosage": "Aucun traitement chimique efficace — lutte par variétés résistantes uniquement.",
            "prevention": "Rotation des cultures, lutte contre la mouche blanche (vecteur), boutures certifiées.",
        },
        {
            "disease_name": "Bactériose du manioc (Xanthomonas)",
            "severity": "modérée",
            "symptoms": "Taches angulaires huileuses sur les feuilles, exsudats gommeux sur les tiges.",
            "remedy": "Éliminer les plants sévèrement atteints, désinfecter les outils de coupe.",
            "dosage": "Bouillie cuprique à 0,3% en prévention, 2 applications à 15 jours d'intervalle.",
            "prevention": "Éviter les blessures mécaniques, espacer suffisamment les plants.",
        },
    ],
    "riz": [
        {
            "disease_name": "Pyriculariose du riz (Magnaporthe oryzae)",
            "severity": "élevée",
            "symptoms": "Taches en forme de losange gris-brun sur les feuilles, nécrose du col de panicule.",
            "remedy": "Fongicide systémique (triazole) dès l'apparition des premières taches.",
            "dosage": "Selon fongicide homologué, généralement 0,5 à 1 L/ha en 2 applications.",
            "prevention": "Éviter l'excès d'azote, variétés tolérantes, bon drainage de la rizière.",
        },
    ],
    "maïs": [
        {
            "disease_name": "Rouille du maïs (Puccinia sorghi)",
            "severity": "modérée",
            "symptoms": "Pustules brun-rougeâtre sur les deux faces des feuilles.",
            "remedy": "Fongicide à base de mancozèbe si l'attaque est précoce et sévère.",
            "dosage": "Mancozèbe 80% : 2 kg/ha dilués dans 400 L d'eau.",
            "prevention": "Rotation culturale, densité de semis adaptée.",
        },
    ],
    "igname": [
        {
            "disease_name": "Anthracnose de l'igname (Colletotrichum)",
            "severity": "élevée",
            "symptoms": "Taches noires anguleuses sur les feuilles, dessèchement des tiges volubiles.",
            "remedy": "Fongicide cuprique préventif dès les premières pluies, destruction des débris infectés.",
            "dosage": "Bouillie bordelaise à 0,5%, toutes les 2 semaines en période humide.",
            "prevention": "Utiliser des semenceaux sains, pratiquer la rotation des cultures.",
        },
    ],
    "banane_plantain": [
        {
            "disease_name": "Cercosporiose noire (Maladie des raies noires)",
            "severity": "élevée",
            "symptoms": "Stries brunes à noires sur les feuilles évoluant en larges plages nécrosées.",
            "remedy": "Effeuillage sanitaire régulier des feuilles atteintes, traitement fongicide en cas de forte pression.",
            "dosage": "Fongicide systémique homologué selon la notice, effeuillage toutes les 2 semaines.",
            "prevention": "Bon espacement des plants pour l'aération, drainage efficace.",
        },
    ],
    "hévéa": [
        {
            "disease_name": "Maladie sud-américaine des feuilles (Microcyclus ulei)",
            "severity": "modérée",
            "symptoms": "Taches huileuses sur jeunes feuilles évoluant en déformations et chute précoce.",
            "remedy": "Fongicide préventif en période de refoliation, clones tolérants recommandés.",
            "dosage": "Selon produit homologué, traitement ciblé sur la période de refoliation.",
            "prevention": "Choix de clones résistants, surveillance en saison des pluies.",
        },
    ],
    "palmier_huile": [
        {
            "disease_name": "Fusariose vasculaire du palmier",
            "severity": "critique",
            "symptoms": "Jaunissement puis dessèchement des feuilles en éventail caractéristique, mort du palmier.",
            "remedy": "Aucun traitement curatif — arrachage et destruction des palmiers atteints obligatoire.",
            "dosage": "Non applicable.",
            "prevention": "Planter des variétés sélectionnées tolérantes, éviter les blessures aux racines.",
        },
    ],
    "coton": [
        {
            "disease_name": "Bactériose du cotonnier",
            "severity": "modérée",
            "symptoms": "Taches anguleuses huileuses sur les feuilles, striures noires sur les tiges.",
            "remedy": "Traitement cuprique préventif, destruction des résidus de récolte après culture.",
            "dosage": "Bouillie cuprique à 0,3%, 2 applications en début de cycle.",
            "prevention": "Semences traitées, rotation culturale.",
        },
    ],
}

# Ajout de quelques maladies animales courantes pour support basique
DISEASE_DATABASE.update({
    "bovin": [
        {
            "disease_name": "Pasteurellose (pneumonie bovine)",
            "severity": "élevée",
            "symptoms": "Toux, difficulté respiratoire, fièvre, abattement.",
            "remedy": "Isoler les animaux malades et traiter avec antibiotiques prescrits par un vétérinaire.",
            "dosage": "Suivre la prescription vétérinaire ; ne pas administrer d'antibiotiques sans avis.",
            "prevention": "Vaccination, bonne ventilation des hangars et isolement des nouveaux sujets.",
        }
    ],
    "volaille": [
        {
            "disease_name": "Coccidiose",
            "severity": "modérée",
            "symptoms": "Diarrhée, abattement, baisse de ponte chez les poules.",
            "remedy": "Traitement anticoccidien adapté et amélioration de l'hygiène du poulailler.",
            "dosage": "Respecter la notice du produit anticoccidien choisi.",
            "prevention": "Nettoyage régulier, litière sèche, rotation des parcours.",
        }
    ],
    "ovin": [
        {
            "disease_name": "Fièvre aphteuse (signe possible)",
            "severity": "critique",
            "symptoms": "Bulle et ulcères buccales, salivation, boiterie.",
            "remedy": "Signaler immédiatement aux autorités vétérinaires ; mesures de contention et d'abattage si confirmée.",
            "dosage": "Non applicable — mesures vétérinaires et réglementaires.",
            "prevention": "Contrôle des mouvements d'animaux, vaccination quand disponible.",
        }
    ],
})

CROP_LABELS = list(DISEASE_DATABASE.keys())

HEALTHY_MESSAGES = [
    "Aucun signe de maladie ou de carence détecté. Le feuillage présente une couleur "
    "et une texture normales.",
]


def _hash_to_float(data: bytes) -> float:
    """Transforme le contenu d'une image en flottant déterministe entre 0 et 1."""
    digest = hashlib.sha256(data).hexdigest()
    return int(digest[:8], 16) / 0xFFFFFFFF


def _diagnose_simulated(image_bytes: bytes, declared_crop: str | None = None) -> dict:
    seed = _hash_to_float(image_bytes)
    rng = random.Random(int(seed * 1_000_000))

    crop_name = declared_crop if declared_crop in DISEASE_DATABASE else rng.choice(CROP_LABELS)

    # ~30% de chances que la plante soit saine, pour crédibiliser la démo
    is_healthy = seed < 0.3

    if is_healthy:
        return {
            "crop_name": crop_name,
            "is_healthy": True,
            "disease_name": "",
            "severity": "faible",
            "symptoms": "",
            "remedy": "",
            "dosage": "",
            "prevention": "Poursuivez une surveillance hebdomadaire et un arrosage régulier.",
            "confidence": round(78 + rng.random() * 18, 1),
            "is_valid_subject": True,
        }

    disease = rng.choice(DISEASE_DATABASE[crop_name])
    return {
        "crop_name": crop_name,
        "is_healthy": False,
        "disease_name": disease["disease_name"],
        "severity": disease["severity"],
        "symptoms": disease["symptoms"],
        "remedy": disease["remedy"],
        "dosage": disease["dosage"],
        "prevention": disease["prevention"],
        "confidence": round(65 + rng.random() * 30, 1),
        "is_valid_subject": True,
    }