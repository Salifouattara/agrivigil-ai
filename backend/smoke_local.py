"""Run against the local demo only. Real provider calls; no simulated responses.

Set AGRIVIGIL_DEMO_PASSWORD in the process environment before running.
The scan, tracking and calculation are kept in the local demo account.
"""
import json
import getpass
import os
from pathlib import Path

import requests

BASE = 'http://127.0.0.1:5185/api'
session = requests.Session()


def call(method, path, **kwargs):
    response = session.request(method, BASE + path, timeout=90, **kwargs)
    if not response.ok:
        try:
            detail = response.json().get('detail', 'Request failed')
        except ValueError:
            detail = 'Non-JSON response'
        raise RuntimeError(f'{path}: HTTP {response.status_code}: {detail}')
    return response.json()


def report(name, data):
    print(json.dumps({'check': name, **data}, ensure_ascii=True), flush=True)


report('health', call('GET', '/health/'))
login = call('POST', '/auth/login/', json={'email': 'demo@monapp.com', 'password': os.environ.get('AGRIVIGIL_DEMO_PASSWORD') or getpass.getpass('Mot de passe du compte demo : ')})
session.headers['Authorization'] = 'Bearer ' + login['access_token']
report('login', {'ok': bool(call('GET', '/auth/me/').get('id'))})
for city in ('Abidjan', 'Yamoussoukro'):
    weather = call('GET', '/weather/', params={'city': city})
    report('weather', {'city': city, 'source': weather['source'], 'temperature': weather['temperature'], 'forecast_days': len(weather['forecast_3days'])})
experts = call('GET', '/experts/')
report('experts', {'count': len(experts)})
calculation = call('POST', '/calculator/', json={'crop_type': 'cacao', 'soil_type': 'latéritique', 'surface_hectares': 2})
report('calculator', {'saved': bool(calculation['id']), 'products': len(calculation['products'])})
image = Path(__file__).parent / 'media/scans/2026/07/plante_saine.jpg'
with image.open('rb') as photo:
    scan = call('POST', '/scans/analyze/', files={'image': ('plante_saine.jpg', photo, 'image/jpeg')}, data={'subject_type': 'plante', 'new_tracking_name': 'Parcelle de démonstration'})
report('real_image_analysis', {'saved': bool(scan['scan_id']), 'crop': scan['crop_name'], 'tracking_saved': bool(scan.get('tracking_id'))})
scans = call('GET', '/scans/')
saved_scan = next(item for item in scans if item['id'] == scan['scan_id'])
media = session.get(saved_scan['image_url'], timeout=10)
assert media.status_code == 200 and media.headers.get('content-type', '').startswith('image/'), 'Local photo not served'
report('health_record_and_photo', {'ok': True, 'scan_count': len(scans)})
advice = call('GET', '/advice/', params={'crop_type': 'cacao'})
report('advice', {'ok': bool(advice['best_practices']), 'ai_enriched': advice.get('ai_enriched', False)})
chat = call('POST', '/experts/messages/', json={'conversation_id': 'chatbot', 'content': 'Comment organiser un carnet hebdomadaire de suivi de mes cultures ? Réponds brièvement.'})
report('ai_chat', {'reply_saved': bool(chat['expert_message']['id']), 'reply_length': len(chat['expert_message']['content'])})
refresh = call('POST', '/auth/token/refresh/', json={'refresh': login['refresh_token']})
refresh_again = call('POST', '/auth/token/refresh/', json={'refresh': refresh['refresh']})
report('session_refresh', {'two_successful_rotations': bool(refresh_again['access'])})
report('complete', {'ok': True})
