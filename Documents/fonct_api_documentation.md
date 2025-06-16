
# 📘 Documentation de l’API Fonctionnelle (fonct_service)

Base URL : `http://fonctservice:8002/api/`

---

## 🏦 Comptes Bancaires

### `GET /comptes/`
**Description :** Récupère tous les comptes de l’utilisateur connecté.

---

### `GET /comptes/user/<utilisateur_id>/`
**Description :** Récupère les comptes appartenant à un utilisateur spécifique (utilisé par les agents).

---

### `GET /comptes/non-valides/`
**Description :** Liste tous les comptes en attente de validation (pour les agents).

---

### `POST /comptes/creer/`
**Description :** Crée un nouveau compte bancaire.

**Corps attendu :**
```json
{
  "numero_compte": "FR761234567890",
  "est_valide": true
}
```

---

### `PUT /comptes/modifier/<compte_id>/`
**Description :** Modifie le RIB d’un compte donné.

**Corps attendu :**
```json
{
  "numero_compte": "FR76000011112222",
  "proprietaire_id": 5
}
```

---

### `DELETE /comptes/supprimer/<compte_id>/`
**Description :** Supprime un compte (utilisateur connecté).

---

### `DELETE /comptes/admin-supprimer/<compte_id>/`
**Description :** Supprime un compte (agent/admin).

---

### `POST /comptes/valider/<compte_id>/`
**Description :** Valide un compte (agent).

---

### `GET /comptes/rib/<numero_compte>/`
**Description :** Recherche un compte via un RIB externe (pour virement inter-utilisateur).

---

## 💳 Opérations Bancaires

### `POST /operations/creer/`
**Description :** Crée une opération (dépôt, retrait, virement).

**Corps exemple :**
```json
{
  "type_operation": "VIREMENT",
  "montant": 100.00,
  "compte_de_debit": 1,
  "compte_de_credit": 2
}
```

---

### `GET /operations/en-attente/`
**Description :** Liste des opérations en attente de validation (pour les agents).

---

### `POST /operations/<operation_id>/valider/`
**Description :** Valide une opération (agent).

---

### `POST /operations/<operation_id>/rejeter/`
**Description :** Rejette une opération (agent).

---

## 🧾 Remarques générales

- Tous les endpoints nécessitent un **token d’authentification** dans l'en-tête :
```http
Authorization: Token <votre_token>
```

- Les opérations bancaires (`VIREMENT`, `DEPOT`, `RETRAIT`) sont validées par un agent avant d'être effectives.

- Les comptes nouvellement créés doivent être validés par un agent.

---
