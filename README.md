# AgriVigil AI — MVP fonctionnel (Vibeathon 2026)

Ce paquet contient une version **fonctionnelle et autonome** de l'application,
reconstruite à partir de l'export Base44 (`agri-vigil-smart`) :

```
agrivigil-ai/
├── frontend/    → React + Vite + Tailwind (l'interface exportée de Base44, adaptée)
└── backend/     → Django REST Framework (nouveau, à connecter au frontend)
```

## Ce qui a changé par rapport à l'export Base44

- Le SDK propriétaire `@base44/sdk` a été retiré. Le frontend utilise
  maintenant `frontend/src/api/apiClient.js`, un client REST classique qui
  parle à `backend/`.
- L'authentification (`AuthContext.jsx`) a été réécrite : la version exportée
  appelait une fonction (`createAxiosClient`) qui n'existait nulle part dans
  le code — elle n'aurait jamais fonctionné en dehors de Base44.
- Le Scan IA appelle **réellement Gemini 2.5 Flash** pour analyser l'image
  envoyée (voir `backend/core/ai_diagnosis.py`). ⚠️ Le projet visait
  initialement "Gemini 1.5 Flash", mais Google a définitivement arrêté toute
  la génération 1.5 mi-2026 (erreur 404 systématique) — j'ai donc basculé sur
  **Gemini 2.5 Flash**, le modèle Flash stable actuellement en production.
- La météo appelle **réellement OpenWeatherMap** (voir `backend/core/weather.py`).

Les deux nécessitent une clé API (voir section suivante). Sans clé, le
diagnostic IA bascule automatiquement sur un moteur simulé (pratique pour
développer sans compte Google), et la météo renvoie une erreur claire plutôt
que d'inventer des données.

## Clés API à configurer

Dans `backend/.env` (copié depuis `.env.example`) :

```
GEMINI_API_KEY=ta_cle_gemini
OPENWEATHER_API_KEY=ta_cle_openweathermap
```

- **Gemini** : crée une clé gratuite sur https://aistudio.google.com/apikey
  (compte Google requis, activation immédiate).
- **OpenWeatherMap** : crée un compte gratuit sur
  https://openweathermap.org/api → onglet "API keys". ⚠️ La clé met
  généralement **jusqu'à 2 heures** à s'activer après la création du compte —
  ne t'inquiète pas si tu as une erreur 401 juste après l'inscription.


## Démarrage rapide

### Lancement officiel pour le jury (une seule commande)

Prérequis : Docker Desktop installé et lancé.

1. Copier le fichier d’environnement de base :

```bash
copy .env.example .env
```

Sur Linux/macOS, remplacer par :

```bash
cp .env.example .env
```

2. Lancer l’application depuis la racine du projet :

```bash
docker compose up --build
```

Une fois démarré :
- Frontend : http://localhost:5173/
- Backend API : http://localhost:8000/api/

> La commande ci-dessus démarre automatiquement le backend Django et le frontend Vite avec la configuration adaptée au projet.

### Lancement manuel (si Docker n’est pas disponible)

#### 1. Backend (Django)

```bash
cd backend
python3 -m venv venv && source venv/bin/activate   # ou .\venv\Scripts\activate sous Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_experts       # crée les 4 experts du Hub Experts
python manage.py createsuperuser    # optionnel, pour /admin/
python manage.py runserver
```

L'API tourne sur http://localhost:8000/api/.

#### 2. Frontend (React/Vite)

```bash
cd frontend
npm install
npm run dev
```

L'appli tourne sur http://localhost:5173/.

## Endpoints REST disponibles

| Méthode | Endpoint                          | Description                                  |
|---------|------------------------------------|-----------------------------------------------|
| POST    | `/api/auth/register/`              | Inscription (déclenche un code OTP)          |
| POST    | `/api/auth/verify-otp/`            | Valide le code, retourne les tokens JWT      |
| POST    | `/api/auth/resend-otp/`            | Renvoie un code                              |
| POST    | `/api/auth/login/`                 | Connexion email/mot de passe                 |
| POST    | `/api/auth/token/refresh/`         | Rafraîchit le token d'accès                  |
| GET     | `/api/auth/me/`                    | Profil de l'utilisateur connecté             |
| POST    | `/api/auth/logout/`                | Déconnexion                                   |
| POST    | `/api/auth/forgot-password/`       | Demande de réinitialisation                  |
| POST    | `/api/auth/reset-password/`        | Réinitialisation du mot de passe             |
| GET/POST| `/api/scans/`                      | Historique des scans / créer un scan brut    |
| POST    | `/api/scans/analyze/`              | Envoie une image → diagnostic IA complet     |
| GET/POST| `/api/alerts/`                     | Alertes sanitaires communautaires            |
| GET/POST| `/api/calculator/`                 | Historique / calcul d'engrais NPK            |
| GET     | `/api/experts/`                    | Annuaire des experts (Hub Experts)            |
| GET/POST| `/api/experts/messages/`           | Messagerie experts (réponse simulée auto)     |
| GET     | `/api/weather/?city=Abidjan`       | Météo agricole du jour                        |
| GET     | `/api/weather/cities/`             | Liste des villes ivoiriennes disponibles      |

**Note sur le "temps réel"** : conformément à ta demande d'endpoints REST
propres pour le MVP, il n'y a pas de WebSocket. Les composants qui
affichaient un flux en direct (alertes communautaires, chat experts) font
un **polling léger** (toutes les 6 secondes) côté frontend — voir la méthode
`subscribe()` dans `apiClient.js`. C'est transparent pour l'utilisateur et
largement suffisant pour un MVP de hackathon ; tu pourras migrer vers Django
Channels plus tard sans changer l'interface des composants.

## Limitations connues du MVP

- Base de données SQLite (suffisant pour la démo ; passer à PostgreSQL/PostGIS
  est prévu dans `settings.py`, commenté et prêt à activer).
- Pas d'envoi réel d'email/SMS pour les codes OTP : ils sont affichés dans la
  console du serveur Django (`[OTP DEMO] ...`). Pratique pour tester sans
  configurer Africa's Talking dans l'immédiat.
- La connexion Google (bouton présent dans l'UI) n'est pas branchée — elle
  affiche un message clair plutôt que de planter.
- Le diagnostic IA (Gemini) et la météo (OpenWeatherMap) nécessitent tes
  propres clés API — voir la section ci-dessus. Sans clé Gemini, le scan
  fonctionne quand même via un moteur de secours simulé ; sans clé
  OpenWeatherMap, l'écran météo renverra une erreur explicite tant que la
  clé n'est pas configurée.
