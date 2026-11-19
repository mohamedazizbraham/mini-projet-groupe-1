# API de gestion des stages

Groupe 1 — Mohamed Aziz BRAHAM, Ghofrane BOUALLEGUE, Dheker KRAIEM et Malek GABSI.

## Livrables et accès

- Code source : https://github.com/mohamedazizbraham/mini-projet-groupe-1
- API : https://mini-projet-groupe-1.onrender.com
- Swagger : https://mini-projet-groupe-1.onrender.com/docs
- Rapport Word modifiable avec captures : [Rapport-authentification.docx](Rapport-authentification.docx).

## Architecture et endpoints

Swagger ou Postman → HTTPS → Render et Docker → Uvicorn et FastAPI → SQLite.

La version 2 propose Sign up et Sign in. Les comptes sont stockés dans SQLite, avec un mot de passe haché par Argon2. La connexion émet un JWT valable 30 minutes. Chaque stage appartient au compte qui le crée ; les listes et opérations sont limitées à ce propriétaire.

| Méthode | Endpoint | Fonction |
|---|---|---|
| POST | /auth/signup | Créer un compte avec username et password en JSON |
| POST | /auth/signin | Se connecter avec les mêmes champs JSON |
| POST | /auth/token | Connexion par formulaire OAuth2 pour Swagger |
| GET | /auth/me | Afficher le compte connecté |
| POST | /stages | Créer son stage |
| GET | /stages | Lister ses stages |
| GET | /stages/{id} | Consulter son stage |
| PUT | /stages/{id} | Remplacer son stage |
| DELETE | /stages/{id} | Supprimer son stage |
| GET | /health | Vérifier la disponibilité |

Après inscription, utiliser Authorize dans Swagger avec les identifiants choisis. Les endpoints de stages et /auth/me exigent un jeton Bearer. JWT_SECRET_KEY est définie hors du dépôt. AUTH_USERNAME et AUTH_PASSWORD_HASH servent uniquement à créer facultativement un compte initial.

SQLite est conservé dans un volume Docker local. Sur Render gratuit, le stockage est éphémère : comptes et stages peuvent disparaître après un redémarrage ou redéploiement. Utiliser des données fictives.

Les captures du 16 novembre 2026 conservées dans le Word illustrent la première version du CRUD et le déploiement initial. Elles précèdent l’ajout de Sign up et Sign in.
