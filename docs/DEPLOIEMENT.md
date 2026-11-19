# Déployer sur Render

## Ajout de l’authentification en version 2

Avant de déployer la version 2, configurer `JWT_SECRET_KEY` dans Environment (clé aléatoire de 32 caractères minimum). `AUTH_USERNAME` et `AUTH_PASSWORD_HASH` sont facultatifs pour créer un compte initial. Les autres comptes se créent avec Sign up. La clé et les hashes restent privés ; ne pas les enregistrer dans GitHub. Voir [AUTHENTIFICATION.md](AUTHENTIFICATION.md). Le contrôle `/health` reste public afin que Render puisse vérifier le service. Les opérations `/stages` exigent désormais une connexion.

## Service déployé pour le groupe

- URL publique : https://mini-projet-groupe-1.onrender.com
- Swagger : https://mini-projet-groupe-1.onrender.com/docs
- Tableau de bord : https://dashboard.render.com/web/srv-dbthi48u01pc73efqdrg
- Configuration observée : Docker, Free, branche `main`, health check `/health`.
- Source : URL du dépôt Git public. Après un push, utiliser **Manual Deploy > Deploy latest commit** pour publier les modifications. L'intégration automatique GitHub n'a pas été étendue.

Les instructions ci-dessous permettent de reproduire le déploiement ; il n'est pas nécessaire de créer un deuxième service.

## Configuration attendue

| Paramètre | Valeur |
|---|---|
| Type | Web Service |
| Dépôt | `mohamedazizbraham/mini-projet-groupe-1` |
| Branche | `main` |
| Runtime / Language | Docker |
| Dockerfile | `./Dockerfile` |
| Root directory | laisser vide |
| Instance | Free |
| Health check | `/health` |
| Variable `DATABASE_PATH` | `/app/data/stages.db` |

Le Dockerfile écoute sur `0.0.0.0` et utilise automatiquement la variable `PORT` fournie par Render. Ne pas remplacer la commande Docker par une commande de développement.

## Parcours manuel

1. Se connecter à https://dashboard.render.com/.
2. Choisir **New > Web Service**.
3. Sélectionner le dépôt GitHub. Si nécessaire, autoriser l'intégration GitHub uniquement pour ce dépôt. Si le dépôt est public, le parcours **Public Git Repository** peut également être utilisé avec son URL.
4. Vérifier les paramètres du tableau et sélectionner le plan **Free**. Ne pas sélectionner de disque ou de service payant pour cet exercice.
5. Lancer **Deploy Web Service** et attendre le statut **Live**.
6. Copier l'URL `https://...onrender.com` indiquée par Render.
7. Ouvrir `/health` puis `/docs` sur cette URL et exécuter le scénario de démonstration.
8. Compléter l'URL et les preuves dans `VALIDATION.md`.

Le fichier `render.yaml` décrit aussi le service pour le parcours **New > Blueprint** si l'intégration GitHub est déjà disponible.

## Vérification à distance

```sh
python scripts/smoke_test.py https://VOTRE-SERVICE.onrender.com
```

Cette commande doit afficher le succès des opérations POST, GET, PUT, DELETE, des erreurs 404 et de la validation 422. La lancer sur le service pédagogique prévu, car elle crée puis supprime un stage fictif.

## Diagnostic

- **Build failed** : ouvrir les logs de construction ; vérifier les versions Python et les dépendances.
- **No open ports / port timeout** : conserver l'écoute `0.0.0.0` et la variable `PORT`.
- **Erreur SQLite / permission denied** : conserver le dossier `/app/data`, créé et attribué à `appuser` par le Dockerfile.
- **Premier accès lent** : laisser le service gratuit se réveiller, puis réessayer.
- **Liste vide après un redémarrage** : c'est une limite du stockage local gratuit ; recréer un stage fictif pour la démonstration.

Sources officielles consultées le 16 novembre 2026 : https://render.com/docs/docker et https://render.com/docs/free.
