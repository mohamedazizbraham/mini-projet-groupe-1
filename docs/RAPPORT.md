# Mini-projet : API de gestion des stages

**Groupe 1 - FIE5, ISIS**

Mohamed Aziz BRAHAM, Ghofrane Bouallegue, Dheker Kraiem et Malek Gbasi

Enseignante : Emna TRIGUI

## 1. Objectif et périmètre

Le projet répond au besoin d'une école souhaitant gérer les stages de ses étudiants. Il fournit une API REST permettant de créer, lister, consulter, remplacer et supprimer les informations d'un stage. L'énoncé demande SQLite, Docker, des tests Swagger ou Postman et un hébergement public Render gratuit.

Le cours traite du cloud, des modèles IaaS/PaaS/SaaS, des API REST, des microservices, de Docker et du déploiement. Le projet applique ces notions à un service unique. Kubernetes et une décomposition en plusieurs services ne sont pas nécessaires pour ce périmètre.

## 2. Conception

La ressource `stage` possède un identifiant entier généré par SQLite, un nom d'étudiant, une entreprise, un intitulé, une date de début et une date de fin. Les dates sont stockées au format ISO. Les textes sont obligatoires et de taille limitée. Une contrainte interdit une fin antérieure au début.

Le client envoie des requêtes HTTP JSON à FastAPI, exécuté par Uvicorn. Les modèles Pydantic valident les données avant leur écriture. Les connexions SQLite sont ouvertes pour les opérations et fermées ensuite ; les modifications sont réalisées dans des transactions. Les requêtes SQL utilisent des paramètres pour séparer données et instructions.

L'API documente ses routes via OpenAPI ; Swagger permet de les essayer directement. Le tableau complet des endpoints et les exemples figurent dans le README.

## 3. Conteneurisation et cloud

Le Dockerfile part de Python 3.12 slim, installe les dépendances, copie l'application et lance le serveur avec un utilisateur non administrateur. Le port est configurable par la variable d'environnement `PORT`, ce qui permet l'exécution locale et sur Render.

Docker Compose monte un volume local pour conserver SQLite. Le service gratuit Render utilise en revanche son système de fichiers éphémère : les données peuvent disparaître lors d'une veille, d'un redémarrage ou d'un redéploiement. Render constitue ici une plateforme PaaS sur un cloud public.

## 4. Validation

La suite automatisée couvre le cycle CRUD, les ressources absentes, les entrées invalides, le remplacement complet, la persistance après réouverture de l'application, la pagination et le traitement de textes ressemblant à du SQL. Un script complémentaire teste une API en fonctionnement par HTTP.

Les résultats effectivement obtenus, distincts des vérifications encore à faire, figurent dans `VALIDATION.md`. Les captures réelles sont référencées dans le même dossier. Le workflow GitHub Actions reproduit les tests et la construction de l'image à chaque envoi de code.

## 5. Limites et améliorations

Cette réalisation est pédagogique : elle ne gère ni authentification, ni autorisations par étudiant, ni sauvegardes. Une utilisation réelle nécessiterait une base durable, la gestion des accès, une stratégie de sauvegarde et une supervision adaptée. SQLite convient au faible volume de l'exercice, mais un déploiement multi-instance nécessiterait de revoir le stockage.

## 6. Répartition proposée du travail

Cette proposition doit être ajustée selon les contributions réellement effectuées ; elle ne constitue pas une attestation du travail individuel.

| Membre | Périmètre proposé | À savoir présenter |
|---|---|---|
| Mohamed Aziz BRAHAM | Intégration, GitHub et coordination du déploiement | Parcours code vers URL publique |
| Ghofrane Bouallegue | Modèle de stage et validation des entrées | Champs, dates et erreurs 422 |
| Dheker Kraiem | Tests API et démonstration Swagger | CRUD, 404 et vérifications |
| Malek Gbasi | Docker, documentation et limites cloud | Image, conteneur, stockage et Render |

Les quatre membres doivent savoir démarrer le projet et expliquer le cycle complet. L'énoncé mentionne un binôme ; le format à quatre membres reste à faire valider par l'enseignante.

## Références

- Énoncé fourni : « Mini-projet : Développer et déployer une API REST dans le Cloud », 2 pages.
- Cours fourni : « Cloud Computing, Microservices & API », Emna TRIGUI, 41 pages ; notamment modèles cloud (p. 7), REST (p. 26), sécurité (p. 29), Docker (p. 32-33) et CI/CD (p. 39-40).
- https://fastapi.tiangolo.com/
- https://render.com/docs/docker
- https://render.com/docs/free
