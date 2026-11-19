# Démonstration Swagger et preuves

## Version 2 avec authentification

Commencer par ouvrir Swagger et exécuter GET `/stages` sans connexion : la réponse doit être 401. Créer un compte avec **POST /auth/signup** (JSON username/password), puis se connecter avec **POST /auth/signin**. Cliquer ensuite **Authorize**, saisir ces identifiants, valider et fermer la fenêtre. GET `/auth/me` doit retourner l’identifiant du compte. Reprendre alors le cycle CRUD décrit ci-dessous. Ne jamais capturer un mot de passe, un jeton ou un en-tête Authorization complet.

Les captures datées du 16 novembre correspondent à la version 1, avant l’ajout de l’authentification. Elles restent une illustration historique du CRUD et du premier déploiement ; elles ne constituent pas une preuve de la protection JWT.

Les captures déjà réalisées sur Render sont fournies dans `captures/` : `01-swagger-public.jpg`, `02-creation-public.jpg`, `03-liste-public.jpg`, `04-modification-public.jpg`, `05-suppression-public.jpg`, `06-introuvable-public.jpg` et `08-render-live.jpg`. Les noms du tableau ci-dessous sont des suggestions pour une nouvelle démonstration. Le cas 422 a été vérifié par le script distant ; sa capture est facultative et n'est pas incluse.

Utiliser `/docs` sur l'API locale ou publique. Pour chaque opération, ouvrir le bloc, cliquer **Try it out**, saisir les paramètres puis **Execute**. Conserver l'identifiant renvoyé à la création.

| Étape | Action | Résultat à vérifier | Capture suggérée |
|---|---|---|---|
| 1 | Ouvrir `/docs` | Les cinq routes métier sont visibles | `01-swagger.png` |
| 2 | POST `/stages` avec l'exemple du README | 201, identifiant attribué, les cinq champs | `02-creation.png` |
| 3 | GET `/stages` | 200, le stage apparaît dans la liste | `03-liste.png` |
| 4 | PUT `/stages/{id}` avec tous les champs et une entreprise modifiée | 200, nouvelle entreprise ; GET confirme la modification | `04-modification.png` |
| 5 | DELETE `/stages/{id}` | 204, corps vide | `05-suppression.png` |
| 6 | GET du même identifiant | 404, `Stage introuvable` | `06-introuvable.png` |
| 7 | POST avec une fin antérieure au début | 422 | `07-validation.png` |
| 8 | Afficher le service Render | Statut Live, URL et déploiement réussi | `08-render.png` |

Placer les captures réelles dans `docs/captures/`. Ne pas présenter une capture locale comme une preuve de déploiement public. Masquer les informations de compte inutiles et ne jamais capturer de secret.

## Déroulé oral, environ 5 minutes

1. **Contexte (40 s)** : gérer des stages grâce à une API HTTP et une base SQLite ; présenter les six informations d'un stage.
2. **Architecture (50 s)** : client Swagger, FastAPI/Uvicorn, SQLite ; expliquer le rôle de Docker et de Render.
3. **Démonstration (2 min)** : création, liste, modification, suppression et 404.
4. **Qualité (40 s)** : montrer les tests et le refus d'une date incohérente.
5. **Cloud et limites (50 s)** : montrer l'URL publique, expliquer la veille et la perte possible des données sur le plan gratuit.

## Questions à préparer

- **Pourquoi FastAPI ?** Validation des entrées, schéma OpenAPI et interface Swagger générés à partir des modèles.
- **Pourquoi SQLite ?** Base relationnelle simple, sans serveur séparé, demandée par l'énoncé.
- **Image ou conteneur ?** Une image est un modèle construit ; un conteneur est une instance en cours d'exécution.
- **Pourquoi 201 et 204 ?** 201 signifie création ; 204 signifie succès sans corps de réponse.
- **PUT ou PATCH ?** Ici PUT remplace l'ensemble des champs ; PATCH servirait à une modification partielle.
- **Render est-il du PaaS ?** Oui, la plateforme prend en charge l'hébergement et le lancement du service sans que le groupe administre une machine virtuelle.
- **Est-ce une architecture de microservices complète ?** Non : c'est un service métier autonome. Plusieurs services séparés ne sont pas nécessaires pour le périmètre de cet exercice.
- **Pourquoi ne pas mettre de vrais étudiants dans la base ?** L'API est ouverte et le stockage gratuit n'est pas durable.
