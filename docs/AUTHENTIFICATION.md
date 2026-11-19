# Authentification de l’API

La version 2 permet de créer un compte (**Sign up**) et de se connecter (**Sign in**). Chaque compte ne peut consulter, modifier ou supprimer que ses propres stages. Les comptes et les hashes des mots de passe sont stockés dans SQLite. Aucun mot de passe ou jeton réel ne doit apparaître dans GitHub, dans le rapport ou dans les captures.

## Sign up et Sign in

1. Ouvrir `/docs`, puis **POST /auth/signup**, **Try it out**.
2. Saisir un corps JSON avec `username` et `password`. L’identifiant accepte 3 à 64 lettres, chiffres, points, tirets ou underscores ; il est normalisé en minuscules. Le mot de passe contient 12 à 128 caractères.
3. Exécuter : HTTP 201 renvoie l’identifiant du compte et son nom, jamais le mot de passe. Un nom déjà utilisé est refusé avec HTTP 409.
4. Ouvrir **POST /auth/signin** et envoyer les mêmes champs JSON : HTTP 200 fournit le jeton JWT de 30 minutes.
5. Pour utiliser les routes avec Swagger sans recopier le jeton, suivre la procédure Authorize ci-dessous. Elle appelle `/auth/token`, équivalent de Sign in au format formulaire OAuth2.

## Connexion avec Swagger

1. Ouvrir `https://mini-projet-groupe-1.onrender.com/docs`.
2. Cliquer **Authorize**.
3. Saisir l’identifiant et le mot de passe du compte créé. Laisser les champs client_id et client_secret vides.
4. Cliquer **Authorize**, puis **Close**.
5. Exécuter les endpoints de stages. Swagger transmet automatiquement le jeton.
6. Après 30 minutes, se reconnecter pour obtenir un nouveau jeton.

## Routes

| Méthode | Route | Accès | Utilisation |
|---|---|---|---|
| POST | `/auth/signup` | Public | Créer un compte depuis un corps JSON |
| POST | `/auth/signin` | Public | Se connecter depuis un corps JSON |
| POST | `/auth/token` | Public | Formulaire `username` et `password`, renvoie un jeton |
| GET | `/auth/me` | JWT requis | Renvoie l’identifiant du compte connecté |
| GET, POST | `/stages` | JWT requis | Liste et création |
| GET, PUT, DELETE | `/stages/{id}` | JWT requis | Consultation, remplacement et suppression |
| GET | `/`, `/health`, `/docs`, `/openapi.json` | Public | Informations du service, santé et documentation |

`/auth/signup` et `/auth/signin` attendent du JSON. Seul `/auth/token` attend `application/x-www-form-urlencoded`. La réponse de connexion contient `access_token`, `token_type: bearer` et `expires_in: 1800`. Les appels métier utilisent l’en-tête `Authorization: Bearer <jeton>`. Un jeton absent, expiré, modifié ou signé par une autre clé est refusé avec HTTP 401. L’accès au stage d’un autre compte renvoie 404 pour ne pas révéler son existence.

## Configuration locale

Après installation de `requirements-dev.txt`, lancer `python scripts/configure_auth.py`. Ce script génère `.env` et `acces-prives.json` et refuse d’écraser une configuration existante. Ne publier aucun de ces fichiers.

Lancer ensuite `docker compose up --build -d`, ou `python scripts/run_local.py` pour un lancement sans Docker. Le script local charge les variables depuis le fichier `.env` généré et écoute uniquement sur la machine locale.

## Configuration Render

Renseigner dans **Environment** : `JWT_SECRET_KEY`, obligatoire. Utiliser une valeur aléatoire de 32 caractères minimum. Sans clé valide, le serveur refuse de démarrer. `AUTH_USERNAME` et `AUTH_PASSWORD_HASH` permettent facultativement de créer un compte initial au premier démarrage ; les inscriptions suivantes utilisent `/auth/signup`. Utiliser les valeurs de `.env` sans les apostrophes. Ne jamais configurer de mot de passe en clair sur Render.

Le compte initial n’est créé que s’il n’existe pas déjà. Modifier son hash d’environnement ne remplace donc pas le mot de passe d’un compte existant en base. Cette version ne propose pas de réinitialisation de mot de passe. Changer `JWT_SECRET_KEY` invalide tous les jetons existants après redéploiement.

## Périmètre

Le mot de passe est vérifié avec Argon2. Les JWT utilisent HS256, avec vérification de la signature, de l’expiration, du sujet, de l’émetteur et du destinataire. Le sujet est l’identifiant du compte en base. Chaque stage possède un propriétaire fixé par le serveur ; le client ne peut pas le choisir. Les comptes ont les mêmes capacités sur leurs propres stages, sans rôle administrateur.

Le bouton Logout de Swagger retire le jeton du navigateur ; il ne révoque pas un jeton déjà copié. Il n’y a pas de renouvellement automatique, de réinitialisation de mot de passe ni de limitation des tentatives de connexion ou d’inscription. Utiliser uniquement des données fictives. SQLite reste éphémère sur Render gratuit : les comptes et les stages peuvent disparaître après une veille ou un redéploiement. Il faut alors recréer son compte.

Référence : https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
