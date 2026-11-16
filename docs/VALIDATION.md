# État de validation - 16 novembre 2026

## Vérifications réalisées

| Vérification | Résultat observé |
|---|---|
| Suite Python | **14 tests réussis** |
| Construction Docker | **Réussie**, image `mini-projet-groupe-1:latest` |
| Conteneur | **Démarré**, utilisateur `appuser` |
| Swagger dans Docker | **Accessible** à `http://127.0.0.1:8000/docs` |
| Test HTTP dans Docker | **Réussi** : création, consultation, liste, modification, suppression, 404 et 422 |
| Déploiement Render | En cours de préparation ; aucune URL publique vérifiée à ce stade |

Un avertissement de dépréciation de Starlette indique que son client de test évolue de `httpx` vers `httpx2`. Il ne fait pas échouer les tests avec les versions fixées dans le projet.

## Résultat HTTP observé

```text
OK GET /health -> 200
OK POST /stages -> 201
OK GET /stages/1 -> 200
OK GET /stages?offset=0&limit=1000 -> 200
OK PUT /stages/1 -> 200
OK GET /stages/1 -> 200
OK POST /stages -> 422
OK DELETE /stages/1 -> 204
OK GET /stages/1 -> 404
OK PUT /stages/1 -> 404
OK DELETE /stages/1 -> 404
SUCCES : cycle CRUD, validation et erreurs 404 verifies.
```

Les identifiants peuvent différer d'une exécution à l'autre.

## Preuves

Les captures dans `captures/` portant la mention `local` montrent l'application exécutée dans Docker sur la machine de développement. Elles ne prouvent pas un déploiement public. La validation Render doit être renseignée après observation du service en ligne et exécution du test distant.
