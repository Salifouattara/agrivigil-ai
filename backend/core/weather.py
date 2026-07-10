"""
Météo réelle via OpenWeatherMap.

Utilise l'API "Current Weather" (données actuelles) et l'API "5 day / 3 hour
forecast" (prévisions), toutes deux disponibles sur le plan gratuit
d'OpenWeatherMap (60 appels/minute, 1000/jour).

>>> Configuration <
Ajoute ta clé dans backend/.env :
    OPENWEATHER_API_KEY=ta_cle_ici
Obtenue gratuitement sur https://openweathermap.org/api (compte gratuit,
la clé peut mettre jusqu'à 2h à s'activer après création).

Si la clé n'est pas configurée, une erreur explicite est levée — pas de
repli silencieux vers des données inventées.
"""

import requests
from django.conf import settings

IVORIAN_CITIES = {
    "Abidjan": (5.36, -4.01),
    "Yamoussoukro": (6.83, -5.28),
    "Bouaké": (7.69, -5.03),
    "Daloa": (6.88, -6.45),
    "San-Pédro": (4.75, -6.64),
    "Man": (7.41, -7.55),
    "Korhogo": (9.46, -5.63),
    "Gagnoa": (6.13, -5.95),
}

BASE_URL = "https://api.openweathermap.org/data/2.5"


class WeatherAPIError(Exception):
    pass


def _condition_from_owm(weather_main: str, pop: float) -> str:
    mapping = {
        "Thunderstorm": "Orageux",
        "Rain": "Pluvieux",
        "Drizzle": "Pluvieux",
        "Clouds": "Nuageux",
        "Clear": "Ensoleillé",
        "Mist": "Brumeux",
        "Haze": "Brumeux",
        "Fog": "Brumeux",
    }
    if weather_main in mapping:
        return mapping[weather_main]
    return "Pluvieux" if pop >= 0.4 else "Ensoleillé"


def _advice_for(temp, humidity, rain_probability):
    if rain_probability >= 60:
        return "Reportez les traitements phytosanitaires : la pluie attendue les rendrait inefficaces."
    if temp >= 32:
        return "Fortes chaleurs : arrosez tôt le matin et évitez les travaux aux champs entre 11h et 16h."
    if humidity >= 85:
        return "Humidité élevée : surveillez les maladies fongiques (pourriture brune, mildiou)."
    return "Conditions favorables aux travaux champêtres et à la fertilisation."


def get_weather(city_name: str, when=None) -> dict:
    api_key = settings.OPENWEATHER_API_KEY
    if not api_key:
        raise WeatherAPIError(
            "OPENWEATHER_API_KEY non configurée. Ajoute ta clé OpenWeatherMap dans le fichier .env "
            "(voir backend/.env.example)."
        )

    lat, lon = IVORIAN_CITIES.get(city_name, IVORIAN_CITIES["Abidjan"])

    current_resp = requests.get(
        f"{BASE_URL}/weather",
        params={"lat": lat, "lon": lon, "appid": api_key, "units": "metric", "lang": "fr"},
        timeout=10,
    )
    if current_resp.status_code != 200:
        raise WeatherAPIError(f"OpenWeatherMap a renvoyé une erreur ({current_resp.status_code}) : {current_resp.text[:200]}")
    current = current_resp.json()

    forecast_resp = requests.get(
        f"{BASE_URL}/forecast",
        params={"lat": lat, "lon": lon, "appid": api_key, "units": "metric", "lang": "fr"},
        timeout=10,
    )
    forecast_data = forecast_resp.json() if forecast_resp.status_code == 200 else {"list": []}

    weather_main = current["weather"][0]["main"]
    rain_probability = round(current.get("pop", 0) * 100) if "pop" in current else (
        60 if weather_main in ("Rain", "Thunderstorm", "Drizzle") else 15
    )

    # Regroupe les prévisions 3h par jour civil pour en tirer un résumé quotidien.
    daily_buckets = {}
    for entry in forecast_data.get("list", []):
        day_key = entry["dt_txt"].split(" ")[0]
        daily_buckets.setdefault(day_key, []).append(entry)

    forecast_3days = {}
    for i, (day_key, entries) in enumerate(list(daily_buckets.items())[1:4], start=1):
        temps = [e["main"]["temp"] for e in entries]
        pops = [e.get("pop", 0) for e in entries]
        main_conditions = [e["weather"][0]["main"] for e in entries]
        dominant = max(set(main_conditions), key=main_conditions.count)
        forecast_3days[f"day{i}"] = {
            "temp_max": round(max(temps), 1),
            "temp_min": round(min(temps), 1),
            "condition": _condition_from_owm(dominant, max(pops)),
        }

    temp = round(current["main"]["temp"], 1)
    humidity = current["main"]["humidity"]

    return {
        "city": city_name,
        "latitude": lat,
        "longitude": lon,
        "temperature": temp,
        "humidity": humidity,
        "wind_speed": round(current.get("wind", {}).get("speed", 0) * 3.6, 1),  # m/s -> km/h
        "condition": _condition_from_owm(weather_main, current.get("pop", 0)),
        "rain_probability": rain_probability,
        "advice_agricole": _advice_for(temp, humidity, rain_probability),
        "forecast_3days": forecast_3days,
        "source": "OpenWeatherMap",
    }