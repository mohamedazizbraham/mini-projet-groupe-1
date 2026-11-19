# État de validation

## Version 2 avec authentification - 19 novembre 2026

Suite locale : **40 tests réussis**. La suite couvre le CRUD authentifié, les identifiants incorrects, les six routes protégées sans jeton, les jetons expirés ou modifiés, le sujet et le destinataire incorrects, l’algorithme non autorisé, la configuration absente et la déclaration OpenAPI.

L’image Docker v2 a également été construite avec succès le 19 novembre. Les tests couvrent aussi Sign up, Sign in, les doublons, la séparation des stages entre comptes, le stockage des hashes et la migration de la base existante.

Version 2 publiée sur Render depuis le commit `de12832`. Swagger public affiche 2.0.0 ; les appels réels depuis Swagger ont confirmé POST /auth/signup → 201 et POST /auth/signin → 200, token_type bearer et expires_in 1800. Le workflow GitHub Actions est réussi : https://github.com/mohamedazizbraham/mini-projet-groupe-1/actions/runs/44700424933.

Le script HTTP local dans Docker confirme aussi le CRUD et l’isolation de deux comptes. Le contrôle distant a été réalisé dans Swagger : le client Python de cette machine rencontre un problème de date du certificat et le client PowerShell reçoit un challenge Cloudflare. Aucune vérification TLS n’a été désactivée. Les résultats ci-dessous sont l’historique v1.

## Historique du 16 novembre 2026

## Vérifications réalisées

| Vérification | Résultat observé |
|---|---|
| Suite Python | **14 tests réussis** |
| Construction Docker | **Réussie**, image `mini-projet-groupe-1:latest` |
| Conteneur | **Démarré**, utilisateur `appuser` |
| Swagger dans Docker | **Accessible** à `http://127.0.0.1:8000/docs` |
| Test HTTP dans Docker | **Réussi** : création, consultation, liste, modification, suppression, 404 et 422 |
| GitHub Actions | **Réussi** : tests Python, construction Docker et test HTTP du conteneur |
| Déploiement Render | **Live**, plan **Free**, runtime **Docker** |
| API publique | **Accessible** : https://mini-projet-groupe-1.onrender.com |
| Swagger public | **Accessible** : https://mini-projet-groupe-1.onrender.com/docs |
| Test HTTP distant | **Réussi** : cycle CRUD, validation 422 et erreurs 404 |

Déploiement initial vérifié sur le commit `64d6449432ad32b541ed67494f8caf33c7efb1f8`.
Exécution GitHub Actions réussie : https://github.com/mohamedazizbraham/mini-projet-groupe-1/actions/runs/43890352570.
Service Render : `srv-dbthi48u01pc73efqdrg`. Le service a été créé à partir du dépôt public et doit être redéployé manuellement après une modification du code.

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

Les captures dans `captures/` portant la mention `local` montrent l'application exécutée dans Docker sur la machine de développement. Les captures `public` montrent les réponses Swagger de l'API hébergée sur Render. `08-render-live.jpg` montre le service gratuit et son statut Live. Le fichier `test-distant.txt` contient le résultat du test HTTP exécuté sur l'URL publique.
