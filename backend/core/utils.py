"""Utilitaires : calcul NPK, géolocalisation et synthèse vocale."""

import math
import os
import threading
import uuid
import urllib.parse
import wave
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

try:
    import torch
    from transformers import VitsModel, VitsTokenizer
except ImportError:  # pragma: no cover - dépendances optionnelles selon l’environnement
    torch = None
    VitsModel = None
    VitsTokenizer = None

VALID_IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif", ".bmp", ".svg", ".tiff", ".tif")


class TTSServiceError(Exception):
    """Erreur levée lorsqu’un service de synthèse vocale ne peut pas générer l’audio."""


_MODEL_CACHE: dict[tuple[str, str], tuple[object, object]] = {}
_MODEL_LOCK = threading.Lock()


def _load_tts_pipeline(model_name: str, token: Optional[str] = None) -> tuple[object, object]:
    """Charge un modèle TTS localement une seule fois par modèle et token."""
    if VitsModel is None or VitsTokenizer is None or torch is None:
        raise TTSServiceError("Les dépendances transformers/torch ne sont pas installées.")

    cache_key = (model_name, token or "")
    cached = _MODEL_CACHE.get(cache_key)
    if cached is not None:
        return cached

    with _MODEL_LOCK:
        cached = _MODEL_CACHE.get(cache_key)
        if cached is not None:
            return cached

        model = VitsModel.from_pretrained(model_name, use_auth_token=token or None)
        tokenizer = VitsTokenizer.from_pretrained(model_name, use_auth_token=token or None)
        model.eval()
        _MODEL_CACHE[cache_key] = (model, tokenizer)
        return _MODEL_CACHE[cache_key]


def _write_wav_file(audio_array, output_path: Path) -> Path:
    """Écrit un tenseur audio au format WAV sur disque."""
    audio_tensor = audio_array.detach().cpu().float().numpy()
    if audio_tensor.ndim > 1:
        audio_tensor = audio_tensor[0]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(output_path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(getattr(audio_array, "sampling_rate", 22050) or 22050)
        pcm = (audio_tensor * 32767).astype("int16").tobytes()
        wav_file.writeframes(pcm)
    return output_path


def synthesize_text(
    text: str,
    token: Optional[str] = None,
    model_name: Optional[str] = None,
    save_to_storage: bool = True,
    use_async: bool = False,
) -> dict:
    """Génère un fichier audio localement via un modèle VITS Hugging Face."""
    if not text or not isinstance(text, str) or not text.strip():
        raise TTSServiceError("Le texte à synthétiser est vide.")

    cleaned_text = text.strip()
    resolved_token = token or getattr(settings, "HUGGINGFACE_API_TOKEN", "") or os.environ.get("HUGGINGFACE_API_TOKEN", "")
    resolved_model = model_name or getattr(settings, "HUGGINGFACE_TTS_MODEL", "") or os.environ.get("HUGGINGFACE_TTS_MODEL", "facebook/mms-tts-bam")

    def _generate() -> dict:
        model, tokenizer = _load_tts_pipeline(resolved_model, resolved_token)
        with torch.no_grad():
            inputs = tokenizer(cleaned_text, return_tensors="pt")
            outputs = model(**inputs)
            audio_array = outputs.waveform[0]

        extension = ".wav"
        file_name = f"tts/{uuid.uuid4().hex}{extension}"
        target_path = Path(settings.MEDIA_ROOT) / file_name
        _write_wav_file(audio_array, target_path)

        if not target_path.exists():
            if save_to_storage:
                audio_bytes = b""
                saved_path = default_storage.save(file_name, ContentFile(audio_bytes))
                audio_url = default_storage.url(saved_path)
                return {"audio_bytes": audio_bytes, "audio_url": audio_url, "path": saved_path}
            return {"audio_bytes": b"", "audio_url": str(target_path), "path": str(target_path)}

        if save_to_storage:
            with target_path.open("rb") as audio_file:
                saved_path = default_storage.save(file_name, ContentFile(audio_file.read()))
            audio_url = default_storage.url(saved_path)
            target_path.unlink(missing_ok=True)
            return {"audio_bytes": b"", "audio_url": audio_url, "path": saved_path}

        return {"audio_bytes": target_path.read_bytes(), "audio_url": str(target_path), "path": str(target_path)}

    if use_async:
        with ThreadPoolExecutor(max_workers=1) as executor:
            return executor.submit(_generate).result()
    return _generate()


def synthesize_text_to_speech(*args, **kwargs) -> dict:
    """Compatibilité avec l’API existante."""
    return synthesize_text(*args, **kwargs)


def ensure_image_extension(value: str, default_extension: str = "avif") -> str:
    """Ajoute une extension d’image si l’URL ou le chemin est tronqué."""
    if not value or not isinstance(value, str):
        return value

    cleaned = value.strip()
    if not cleaned:
        return cleaned

    parsed = urllib.parse.urlsplit(cleaned)
    path = urllib.parse.unquote(parsed.path or "")

    if any(path.lower().endswith(ext) for ext in VALID_IMAGE_EXTENSIONS):
        return cleaned

    if path.endswith("/"):
        path = path.rstrip("/")

    if "." in path.split("/")[-1]:
        return cleaned

    suffix = default_extension if not default_extension.startswith(".") else default_extension
    path = f"{path}.{suffix}"

    if parsed.scheme and parsed.netloc:
        return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, path, parsed.query, parsed.fragment))

    return path

FERTILIZER_DATA = {
    "cacao": {"base": {"N": 60, "P": 30, "K": 80}, "soil": {
        "argileux": {"N": 0.9, "P": 1.0, "K": 0.85}, "sableux": {"N": 1.2, "P": 1.1, "K": 1.3},
        "limoneux": {"N": 1.0, "P": 1.0, "K": 1.0}, "latéritique": {"N": 1.1, "P": 1.2, "K": 1.0},
        "tourbeux": {"N": 0.8, "P": 1.1, "K": 1.1},
    }},
    "café": {"base": {"N": 80, "P": 40, "K": 60}, "soil": {
        "argileux": {"N": 0.9, "P": 1.0, "K": 0.9}, "sableux": {"N": 1.2, "P": 1.2, "K": 1.2},
        "limoneux": {"N": 1.0, "P": 1.0, "K": 1.0}, "latéritique": {"N": 1.1, "P": 1.15, "K": 1.05},
        "tourbeux": {"N": 0.85, "P": 1.1, "K": 1.1},
    }},
    "manioc": {"base": {"N": 40, "P": 20, "K": 100}, "soil": {
        "argileux": {"N": 0.85, "P": 0.9, "K": 0.8}, "sableux": {"N": 1.15, "P": 1.2, "K": 1.3},
        "limoneux": {"N": 1.0, "P": 1.0, "K": 1.0}, "latéritique": {"N": 1.1, "P": 1.15, "K": 1.0},
        "tourbeux": {"N": 0.8, "P": 1.0, "K": 1.1},
    }},
    "riz": {"base": {"N": 90, "P": 45, "K": 45}, "soil": {
        "argileux": {"N": 0.95, "P": 1.0, "K": 0.9}, "sableux": {"N": 1.2, "P": 1.15, "K": 1.25},
        "limoneux": {"N": 1.0, "P": 1.0, "K": 1.0}, "latéritique": {"N": 1.1, "P": 1.2, "K": 1.05},
        "tourbeux": {"N": 0.85, "P": 1.05, "K": 1.1},
    }},
    "maïs": {"base": {"N": 100, "P": 50, "K": 50}, "soil": {
        "argileux": {"N": 0.9, "P": 0.95, "K": 0.85}, "sableux": {"N": 1.2, "P": 1.2, "K": 1.3},
        "limoneux": {"N": 1.0, "P": 1.0, "K": 1.0}, "latéritique": {"N": 1.1, "P": 1.15, "K": 1.0},
        "tourbeux": {"N": 0.85, "P": 1.05, "K": 1.1},
    }},
    "igname": {"base": {"N": 50, "P": 25, "K": 90}, "soil": {
        "argileux": {"N": 0.85, "P": 0.9, "K": 0.8}, "sableux": {"N": 1.15, "P": 1.2, "K": 1.25},
        "limoneux": {"N": 1.0, "P": 1.0, "K": 1.0}, "latéritique": {"N": 1.1, "P": 1.15, "K": 1.0},
        "tourbeux": {"N": 0.8, "P": 1.05, "K": 1.1},
    }},
    "banane_plantain": {"base": {"N": 70, "P": 30, "K": 120}, "soil": {
        "argileux": {"N": 0.9, "P": 0.95, "K": 0.85}, "sableux": {"N": 1.15, "P": 1.15, "K": 1.3},
        "limoneux": {"N": 1.0, "P": 1.0, "K": 1.0}, "latéritique": {"N": 1.1, "P": 1.15, "K": 1.0},
        "tourbeux": {"N": 0.85, "P": 1.05, "K": 1.1},
    }},
    "hévéa": {"base": {"N": 55, "P": 35, "K": 45}, "soil": {
        "argileux": {"N": 0.9, "P": 1.0, "K": 0.9}, "sableux": {"N": 1.15, "P": 1.15, "K": 1.2},
        "limoneux": {"N": 1.0, "P": 1.0, "K": 1.0}, "latéritique": {"N": 1.1, "P": 1.1, "K": 1.05},
        "tourbeux": {"N": 0.85, "P": 1.05, "K": 1.1},
    }},
    "palmier_huile": {"base": {"N": 60, "P": 30, "K": 100}, "soil": {
        "argileux": {"N": 0.9, "P": 0.95, "K": 0.85}, "sableux": {"N": 1.2, "P": 1.2, "K": 1.3},
        "limoneux": {"N": 1.0, "P": 1.0, "K": 1.0}, "latéritique": {"N": 1.1, "P": 1.15, "K": 1.0},
        "tourbeux": {"N": 0.85, "P": 1.05, "K": 1.1},
    }},
    "coton": {"base": {"N": 80, "P": 40, "K": 40}, "soil": {
        "argileux": {"N": 0.9, "P": 0.95, "K": 0.85}, "sableux": {"N": 1.2, "P": 1.2, "K": 1.25},
        "limoneux": {"N": 1.0, "P": 1.0, "K": 1.0}, "latéritique": {"N": 1.1, "P": 1.15, "K": 1.0},
        "tourbeux": {"N": 0.85, "P": 1.05, "K": 1.1},
    }},
}


def calculate_fertilizer(crop_type: str, soil_type: str, hectares: float) -> dict:
    crop = FERTILIZER_DATA.get(crop_type)
    if not crop:
        raise ValueError(f"Culture inconnue: {crop_type}")
    mod = crop["soil"].get(soil_type, {"N": 1, "P": 1, "K": 1})
    return {
        "nitrogen_kg": round(crop["base"]["N"] * mod["N"] * hectares, 1),
        "phosphorus_kg": round(crop["base"]["P"] * mod["P"] * hectares, 1),
        "potassium_kg": round(crop["base"]["K"] * mod["K"] * hectares, 1),
    }


# Prix indicatifs en FCFA/kg (marché ivoirien, ordre de grandeur MVP)
FERTILIZER_PRODUCTS = [
    {"id": "npk_15_15_15", "name": "NPK 15-15-15", "price_fcfa_kg": 350, "N": 0.15, "P": 0.15, "K": 0.15},
    {"id": "npk_12_24_12", "name": "NPK 12-24-12", "price_fcfa_kg": 380, "N": 0.12, "P": 0.24, "K": 0.12},
    {"id": "uree", "name": "Urée (46% N)", "price_fcfa_kg": 280, "N": 0.46, "P": 0.0, "K": 0.0},
    {"id": "smp", "name": "Superphosphate (18% P)", "price_fcfa_kg": 320, "N": 0.0, "P": 0.18, "K": 0.0},
    {"id": "kcl", "name": "Chlorure de potassium (60% K)", "price_fcfa_kg": 400, "N": 0.0, "P": 0.0, "K": 0.60},
]


def _estimate_product_mix(n_kg: float, p_kg: float, k_kg: float) -> list[dict]:
    """Estime un mix d'engrais commercial pour couvrir les besoins NPK."""
    products = []
    remaining_n, remaining_p, remaining_k = n_kg, p_kg, k_kg

    npk = FERTILIZER_PRODUCTS[0]
    ratios = []
    if remaining_n > 0 and npk["N"]:
        ratios.append(remaining_n / npk["N"])
    if remaining_p > 0 and npk["P"]:
        ratios.append(remaining_p / npk["P"])
    if remaining_k > 0 and npk["K"]:
        ratios.append(remaining_k / npk["K"])
    npk_total = min(ratios) if ratios else 0
    if npk_total > 0:
        qty = round(npk_total, 1)
        products.append({
            "name": npk["name"],
            "quantity_kg": qty,
            "unit_price_fcfa": npk["price_fcfa_kg"],
            "subtotal_fcfa": round(qty * npk["price_fcfa_kg"]),
        })
        remaining_n = max(0, remaining_n - qty * npk["N"])
        remaining_p = max(0, remaining_p - qty * npk["P"])
        remaining_k = max(0, remaining_k - qty * npk["K"])

    if remaining_n > 5:
        uree = FERTILIZER_PRODUCTS[2]
        qty = round(remaining_n / uree["N"], 1)
        products.append({
            "name": uree["name"],
            "quantity_kg": qty,
            "unit_price_fcfa": uree["price_fcfa_kg"],
            "subtotal_fcfa": round(qty * uree["price_fcfa_kg"]),
        })
        remaining_n = 0

    if remaining_p > 3:
        smp = FERTILIZER_PRODUCTS[3]
        qty = round(remaining_p / smp["P"], 1)
        products.append({
            "name": smp["name"],
            "quantity_kg": qty,
            "unit_price_fcfa": smp["price_fcfa_kg"],
            "subtotal_fcfa": round(qty * smp["price_fcfa_kg"]),
        })

    if remaining_k > 5:
        kcl = FERTILIZER_PRODUCTS[4]
        qty = round(remaining_k / kcl["K"], 1)
        products.append({
            "name": kcl["name"],
            "quantity_kg": qty,
            "unit_price_fcfa": kcl["price_fcfa_kg"],
            "subtotal_fcfa": round(qty * kcl["price_fcfa_kg"]),
        })

    return products


def _application_plan(crop_type: str, hectares: float) -> list[dict]:
    """Plan de fractionnement des apports selon la culture."""
    plans = {
        "cacao": [
            {"phase": "Début saison des pluies", "share_pct": 40, "timing": "Mars-Avril"},
            {"phase": "Mi-saison", "share_pct": 35, "timing": "Juin-Juillet"},
            {"phase": "Fin saison", "share_pct": 25, "timing": "Septembre-Octobre"},
        ],
        "riz": [
            {"phase": "Repiquage", "share_pct": 30, "timing": "J0"},
            {"phase": "Tallage", "share_pct": 40, "timing": "J+30"},
            {"phase": "Montaison", "share_pct": 30, "timing": "J+60"},
        ],
        "maïs": [
            {"phase": "Semis", "share_pct": 40, "timing": "J0"},
            {"phase": "6-8 feuilles", "share_pct": 60, "timing": "J+35"},
        ],
    }
    default = [
        {"phase": "Premier apport", "share_pct": 40, "timing": "Début cycle"},
        {"phase": "Deuxième apport", "share_pct": 35, "timing": "Mi-cycle"},
        {"phase": "Troisième apport", "share_pct": 25, "timing": "Fin cycle"},
    ]
    return plans.get(crop_type, default)


def calculate_fertilizer_detailed(crop_type: str, soil_type: str, hectares: float) -> dict:
    """Calcul NPK enrichi avec produits, coûts et plan d'application."""
    npk = calculate_fertilizer(crop_type, soil_type, hectares)
    products = _estimate_product_mix(npk["nitrogen_kg"], npk["phosphorus_kg"], npk["potassium_kg"])
    total_cost = sum(p["subtotal_fcfa"] for p in products)
    application_plan = _application_plan(crop_type, hectares)

    for phase in application_plan:
        phase["nitrogen_kg"] = round(npk["nitrogen_kg"] * phase["share_pct"] / 100, 1)
        phase["phosphorus_kg"] = round(npk["phosphorus_kg"] * phase["share_pct"] / 100, 1)
        phase["potassium_kg"] = round(npk["potassium_kg"] * phase["share_pct"] / 100, 1)

    soil_notes = {
        "argileux": "Sol lourd : fractionner les apports et éviter les doses uniques élevées.",
        "sableux": "Sol léger : privilégier des apports fractionnés et le compost.",
        "limoneux": "Sol équilibré : respecter le calendrier cultural standard.",
        "latéritique": "Sol latéritique : compléter avec matière organique (compost 5 t/ha).",
        "tourbeux": "Sol riche : réduire légèrement les apports azotés si excès de végétation.",
    }

    return {
        **npk,
        "products": products,
        "total_cost_fcfa": total_cost,
        "application_plan": application_plan,
        "soil_note": soil_notes.get(soil_type, ""),
        "recommendation_summary": (
            f"Pour {hectares} ha de {crop_type} sur sol {soil_type} : "
            f"{npk['nitrogen_kg']} kg N, {npk['phosphorus_kg']} kg P, {npk['potassium_kg']} kg K. "
            f"Coût estimé : {total_cost:,} FCFA.".replace(",", " ")
        ),
    }


def haversine_km(lat1, lon1, lat2, lon2) -> float:
    """Distance en kilomètres entre deux points GPS (formule de Haversine)."""
    if None in (lat1, lon1, lat2, lon2):
        return 0.0
    r = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return round(r * 2 * math.asin(math.sqrt(a)), 1)
