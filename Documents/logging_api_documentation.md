
# 📝 Documentation de l’API Logging (logging_service)

Base URL : `http://loggingservice:8003/`

---

## 🔄 `POST /logs/create/`
**Description :** Publie un log via NATS (Ne l’enregistre pas en base) publie juste sur le nats.

**Corps attendu :**
```json
{
  "level": "INFO",                // ou "ERROR", "WARNING", etc.
  "type_action": "VIREMENT",      // ou "DEPOT", "RETRAIT", etc.
  "message": "Opération réussie",
  "visibilite": "PUBLIC",         // ou "PRIVE"
  "identifiant_utilisateur": 42,
  "compte_id": 1,
  "montant": 200.0
}
```

**Réponse :**
```json
{
  "message": "Log publié via NATS"
}
```

**Codes :**
- `201 Created` si succès
- `400 Bad Request` en cas d’erreur de validation

---

## 📥 `GET /logs/`
**Description :** Récupère une liste des logs enregistrés en base de données.

### 🔎 Paramètres de filtrage optionnels :
- `level`: filtre par niveau (ex: `ERROR`, `INFO`, etc.)
- `type_action`: type d’action (ex: `VIREMENT`, `DEPOT`, etc.)
- `visibilite`: `PUBLIC` ou `PRIVE`
- `identifiant_utilisateur`: filtre par ID utilisateur
- `limit`: limite le nombre de résultats (par défaut : 100)

**Réponse :**
```json
[
  {
    "id": 1,
    "level": "INFO",
    "type_action": "VIREMENT",
    "message": "Virement de 200€ effectué",
    "visibilite": "PUBLIC",
    "identifiant_utilisateur": 42,
    "compte_id": 1,
    "montant": 200.0,
    "created_at": "2025-06-16T14:32:10Z"
  },
  ...
]
```

---

## 🔐 Sécurité
Aucune authentification requise par défaut, mais peut être ajoutée via reverse proxy ou décorateur Django si besoin.

---

## 🚀 Notes Techniques
- La publication NATS utilise le sujet : `log.<visibilite>.<level>` (ex: `log.public.info`).
- Les logs affichés sont triés par date décroissante.
- Le `LogCreateSerializer` ne sauvegarde pas les logs, mais les envoie via NATS.

---