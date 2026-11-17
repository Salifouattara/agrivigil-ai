# AgriVigil AI

Application React/Vite et API Django REST pour le diagnostic visuel, le carnet de suivi, les alertes communautaires, les conseils, la météo et le calcul d'engrais.

## Démonstration locale sur Windows

Depuis ce dossier, dans PowerShell :

```powershell
.\Start-AgriVigil.ps1
```

- Application : http://127.0.0.1:5173/
- État du backend : http://127.0.0.1:5185/api/health/
- Compte de démonstration : `demo@monapp.com`, avec le mot de passe fourni par le propriétaire.
- Arrêt : `.\Stop-AgriVigil.ps1` ; puis relancer après modification de `backend/.env`.
- Les processus démarrent en arrière-plan. Les journaux sont dans `.local/`.
- La base `backend/db.sqlite3` et les photos restent sur cet ordinateur.
- Une connexion Internet est nécessaire pour Gemini et OpenWeatherMap, même en local.

Le lanceur vérifie les ports pour éviter d'interférer avec une autre application. Il exécute les migrations et vérifie la disponibilité des deux serveurs. Il utilise les installations Python et Node présentes sur la machine et les dépendances déjà installées.

## Configuration

Les secrets se trouvent uniquement dans `backend/.env`, exclu de Git. Le modèle de fichier est `backend/.env.example`.

Variables utiles :

- `DJANGO_SECRET_KEY` : secret Django aléatoire.
- `GEMINI_API_KEY` : clé Gemini.
- `GEMINI_MODEL` : modèle à utiliser, `gemini-2.5-flash` par défaut.
- `OPENWEATHER_API_KEY` : clé météo.
- `DATABASE_URL` : facultatif ; SQLite local par défaut, PostgreSQL possible en ligne.
- `DJANGO_ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS` : hôtes et origines autorisés.
- `DJANGO_DEBUG=True` pour le développement local uniquement.

Le frontend utilise `http://127.0.0.1:5185` en développement. `VITE_API_BASE_URL` permet de choisir une autre API. Les clés Gemini et météo ne doivent jamais être placées dans une variable `VITE_`.

Sans clé Gemini, l'application indique que l'analyse est indisponible. Les parcours de diagnostic, d'analyse du sol et de conversation ne génèrent plus de résultats simulés. Les conseils du référentiel restent consultables si leur enrichissement IA échoue. La météo conserve ses résultats dix minutes pour limiter les appels.

## Vérifications

Backend :

```powershell
cd backend
python manage.py check
python manage.py test core.tests --noinput
```

Frontend :

```powershell
cd frontend
npm run build
npm run lint
npm run typecheck
```

Test réel du compte local, serveurs démarrés :

```powershell
cd backend
python smoke_local.py
```

Ce test demande le mot de passe du compte de démonstration et effectue de vrais appels aux services. Il conserve un scan, un suivi, un calcul d'engrais et une conversation dans le compte local. Il vérifie aussi la lecture de la photo sauvegardée et le renouvellement des sessions. Ne pas utiliser ce script sur une API de production.

## Parcours de présentation

1. Se connecter au compte démo.
2. Consulter le scan de cacao et le carnet de suivi, puis charger une autre photo.
3. Montrer les signalements et leurs détails dans Communauté.
4. Comparer la météo de plusieurs villes et les prévisions à trois jours.
5. Calculer les besoins NPK d'une parcelle.
6. Consulter les conseils par culture et poser une question au chatbot.

Les diagnostics visuels et calculs servent d'aide à la décision ; ils ne remplacent pas une analyse de laboratoire ou l'avis d'un professionnel de terrain.

## Docker et hébergement

`docker compose up --build` charge également `backend/.env` et expose les mêmes ports locaux. Ne pas lancer Docker et le lanceur Windows simultanément. Le parcours Docker n'a pas été revalidé pendant la préparation locale.

Les modifications de cette préparation sont locales. Le site Vercel et le service Railway ne sont pas redéployés par les scripts. Pour un hébergement Django distinct, configurer l'URL de l'API, CORS, les secrets, une base persistante et le stockage des médias avant de publier.

## Limites actuelles

L'envoi de mails/SMS, la connexion Google et la synthèse vocale Dioula ne sont pas configurés pour la démonstration. Utiliser le compte démo existant. La lecture vocale française dépend du navigateur et des voix installées. Le contrôle visuel automatisé du navigateur a été indisponible pendant cette intervention ; les validations réalisées portent sur le code, la compilation et les appels API réels.


## Version de présentation — novembre 2026

- Interface adaptative : navigation latérale sur ordinateur, barre basse sur mobile ; plus de cadre de téléphone sur grand écran.
- Connexion de démonstration préremplissable ; chargement des pages à la demande.
- Hub Experts : portraits locaux réparés, avatar de secours et profils d’exemple signalés comme tels. Leurs contacts restent désactivés tant que les professionnels ne sont pas validés.
- Communauté : signalements de l’API, sans fausse épidémie ni foyers inventés.

### PythonAnywhere gratuit

La release est générée par `python deploy/build_release.py`. Elle exclut les secrets, bases de données et photos de scans. Le script `deploy/setup_pythonanywhere.py` installe les dépendances ciblées, conserve une sauvegarde de la base, applique les migrations et collecte les fichiers statiques. L’ancienne installation `/home/Salif/agrivigil-ai` est préservée ; la nouvelle release est dans `/home/Salif/agrivigil-release-20261117`.

Configuration Web prévue : Python 3.13, virtualenv `/home/Salif/agrivigil-release-20261117/.venv`, WSGI fourni dans `deploy/pythonanywhere_wsgi.py`, mappings `/static/` vers `backend/staticfiles` et `/media/` vers `backend/media`. Le fichier `backend/.env` distant contient les secrets, `DJANGO_DEBUG=False`, les hôtes autorisés et l’origine Vercel. Aucune clé Gemini ou météo ne doit se trouver dans les variables `VITE_*`.

L’offre gratuite comporte un seul worker, 512 MiB de stockage, des accès réseau sortants limités et une expiration du site à renouveler manuellement. Elle convient à une démonstration à faible charge, avec la version locale comme solution de repli. Documentation : https://help.pythonanywhere.com/pages/FreeAccountsFeatures/

### À compléter avant un usage public durable

- Valider les profils et partenariats du Hub Experts.
- Brancher un fournisseur d’e-mails pour les codes d’inscription et de récupération ; la connexion Google reste à intégrer et son bouton n’est plus affiché.
- Valider les recommandations agricoles sur le terrain et organiser la modération des signalements.
- Automatiser les sauvegardes et définir les quotas d’utilisation de l’IA.
- Tester et compléter les langues locales et la synthèse vocale sur les appareils visés.
