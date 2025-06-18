
# 📚 API d'Authentification – Documentation

Base URL : `/api/auth/`

## 🔐 Authentification

### `POST /api/auth/register/`
**Description :** Inscription d’un nouvel utilisateur.

**Corps attendu :**
```json
{
  "username": "jdoe",
  "email": "jdoe@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "password": "strongpassword123",
  "confirm_password": "strongpassword123",
  "phone_number": "+33600000000",
  "address": "1 rue de la Paix",
  "role": "CLIENT"  // ou "AGENT" si superadmin
}
```

**Règles de validation :**
- Le mot de passe doit être conforme aux règles Django.
- Les rôles valides : `CLIENT`, `AGENT`. Le rôle `SUPER_USER` est interdit.
- Seul un superutilisateur peut créer un agent.

**Réponse :** `201 Created` ou `400 Bad Request` (erreurs de validation).

---

### `POST /api/auth/login/`
**Description :** Connexion d’un utilisateur.

**Corps attendu :**
```json
{
  "username": "jdoe",
  "password": "strongpassword123"
}
```

**Réponse :**
```json
{
  "token": "..." 
}
```

**Erreurs possibles :**
- Mauvais identifiants.
- Compte désactivé.

---

### `POST /api/auth/logout/`
**Description :** Déconnexion de l’utilisateur.

**Réponse :** `200 OK`

---

### `POST /api/auth/password/reset/`
**Description :** Réinitialisation du mot de passe pour un utilisateur connecté.

**Corps attendu :**
```json
{
  "old_password": "oldpass123",
  "new_password": "newstrongpass",
  "confirm_password": "newstrongpass"
}
```

**Réponse :** `200 OK` ou `400 Bad Request`

---

## 👤 Profil utilisateur

### `GET /api/auth/profile/`
**Description :** Récupération du profil de l'utilisateur connecté.

**Réponse :**
```json
{
  "id": 1,
  "username": "jdoe",
  "email": "jdoe@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+33600000000",
  "address": "1 rue de la Paix",
  "role": "CLIENT",
  "role_display": "Client",
  "created_at": "2025-06-01T10:00:00Z",
  "updated_at": "2025-06-15T15:30:00Z"
}
```

---

## 🛠️ Gestion des utilisateurs (Agents uniquement)

### `GET /api/auth/users/`
**Description :** Liste de tous les utilisateurs (vue agent).

**Réponse :**
```json
[
  {
    "id": 2,
    "username": "jane",
    "email": "jane@example.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "role": "CLIENT",
    "role_display": "Client",
    "is_active": true,
    "created_at": "2025-06-10T12:00:00Z"
  }
]
```

---

### `GET /api/auth/users/<user_id>/`
**Description :** Récupération des détails d’un utilisateur.

**Réponse :** Données complètes du profil utilisateur.

---

### `GET /api/auth/users/pending/`
**Description :** Liste des utilisateurs en attente de validation (`is_active=False`).

**Réponse :** Liste filtrée d'utilisateurs non encore validés.

---

### `POST /api/auth/users/<user_id>/validate/`
**Description :** Valider un utilisateur en attente.

**Corps optionnel :**
```json
{
  "is_active": true,
  "reason": "Validation manuelle"
}
```

**Réponse :** `200 OK`

---

### `DELETE /api/auth/users/<user_id>/reject/`
**Description :** Rejeter et supprimer un utilisateur en attente.

**Réponse :** `204 No Content`

---

### `POST /api/auth/agents/create/`
**Description :** Création d’un agent (réservé au superadmin).

**Corps attendu :** Identique à l'inscription, avec le rôle `"AGENT"`.

**Réponse :** `201 Created` ou `403 Forbidden`

---

## 🔍 Vérification de Token

### `POST /api/auth/users/validate-token/`
**Description :** Vérifie la validité d’un token.

**Corps attendu :**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJh..."
}
```

**Réponse :**
```json
{
  "valid": true,
  "user_id": 1,
  "username": "jdoe",
  "role": "CLIENT"
}
```

**Erreurs possibles :**
- `401 Unauthorized` si token invalide ou expiré.

---
