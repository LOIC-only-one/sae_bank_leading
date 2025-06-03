🎯 Résumé rapide de ce que tu dois savoir
✅ Si tes APIs sont stateless et exposées publiquement (ce qui est souvent le cas en microservices) :
Tu n’as pas besoin de CSRF car tu n’utilises pas de cookies pour l’authentification.

➡️ Tu dois désactiver la vérification CSRF sur tes APIs.
➡️ Et utiliser un autre mécanisme d’authentification, comme un token JWT, ou un token d’API.


