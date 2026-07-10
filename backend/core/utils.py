"""Utilitaires : calcul NPK (identique à src/lib/theme.js du frontend) et géolocalisation."""

import math

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
