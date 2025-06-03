# Documentation API - Gestion des Utilisateurs

## Vue d'ensemble
Cette API REST permet la gestion complète des utilisateurs avec un système de rôles (Client, Agent, Superutilisateur) et de validation des comptes.

---

## 🔐 Authentification

### POST `/register/`
**Inscription d'un nouvel utilisateur**

#### Permissions
- Accessible à tous (AllowAny)

#### Paramètres du corps de requête
```json
{
  "username": "string",      // Nom d'utilisateur (requis)
  "email": "string",         // Adresse email (requis)
  "password": "string",      // Mot de passe (requis)
  "first_name": "string",    // Prénom (optionnel)
  "last_name": "string"      // Nom de famille (optionnel)
}
```

#### Réponses
- **201 Created** - Compte créé avec succès
```json
{
  "message": "Compte créé avec succès",
  "user": {
    "id": 1,
    "username": "utilisateur",
    "email": "email@example.com",
    "role": "CLIENT",
    "is_active": false
  }
}
```
- **400 Bad Request** - Erreur de validation

---

### POST `/login/`
**Connexion d'un utilisateur**

#### Permissions
- Accessible à tous (AllowAny)

#### Paramètres du corps de requête
```json
{
  "username": "string",  // Nom d'utilisateur (requis)
  "password": "string"   // Mot de passe (requis)
}
```

#### Réponses
- **200 OK** - Connexion réussie
```json
{
  "message": "Connexion réussie",
  "user": {
    "id": 1,
    "username": "utilisateur",
    "email": "email@example.com",
    "role": "CLIENT",
    "role_display": "Client",
    "is_active": true
  }
}
```
- **400 Bad Request** - Identifiants invalides ou erreur de validation

---

### POST `/logout/`
**Déconnexion de l'utilisateur**

#### Permissions
- Authentification requise (IsAuthenticated)

#### Paramètres
Aucun paramètre requis

#### Réponses
- **200 OK** - Déconnexion réussie
```json
{
  "message": "Déconnexion réussie"
}
```

---

## 👤 Gestion du Profil

### GET `/profile/`
**Consultation du profil utilisateur**

#### Permissions
- Authentification requise (IsAuthenticated)

#### Paramètres
Aucun paramètre requis

#### Réponses
- **200 OK** - Données du profil
```json
{
  "id": 1,
  "username": "utilisateur",
  "email": "email@example.com",
  "first_name": "Prénom",
  "last_name": "Nom",
  "role": "CLIENT",
  "is_active": true
}
```

---

### PUT `/profile/`
**Modification du profil utilisateur**

#### Permissions
- Authentification requise (IsAuthenticated)

#### Paramètres du corps de requête (tous optionnels)
```json
{
  "username": "string",     // Nouveau nom d'utilisateur
  "email": "string",        // Nouvelle adresse email
  "first_name": "string",   // Nouveau prénom
  "last_name": "string"     // Nouveau nom de famille
}
```

#### Réponses
- **200 OK** - Profil mis à jour
```json
{
  "message": "Profil mis à jour avec succès",
  "user": {
    "id": 1,
    "username": "nouveau_utilisateur",
    "email": "nouvel_email@example.com",
    "first_name": "Nouveau Prénom",
    "last_name": "Nouveau Nom",
    "role": "CLIENT",
    "is_active": true
  }
}
```
- **400 Bad Request** - Erreur de validation

---

## 👥 Gestion des Utilisateurs (Agent/Superutilisateur)

### GET `/users/`
**Liste des utilisateurs**

#### Permissions
- Authentification requise (IsAuthenticated)
- Rôle Agent ou Superutilisateur requis

#### Paramètres de requête (optionnels)
- `role` : Filtre par rôle (CLIENT, AGENT, SUPERUSER)
  - Exemple : `/users/?role=CLIENT`

#### Comportement selon le rôle
- **Agent** : Ne peut voir que les clients
- **Superutilisateur** : Peut voir tous les utilisateurs

#### Réponses
- **200 OK** - Liste des utilisateurs
```json
[
  {
    "id": 1,
    "username": "client1",
    "email": "client1@example.com",
    "role": "CLIENT",
    "is_active": true
  },
  {
    "id": 2,
    "username": "client2",
    "email": "client2@example.com",
    "role": "CLIENT",
    "is_active": false
  }
]
```
- **403 Forbidden** - Permission refusée

---

### GET `/pending-users/`
**Liste des comptes en attente de validation**

#### Permissions
- Authentification requise (IsAuthenticated)
- Rôle Agent ou Superutilisateur requis

#### Paramètres
Aucun paramètre requis

#### Réponses
- **200 OK** - Liste des utilisateurs en attente
```json
{
  "count": 2,
  "users": [
    {
      "id": 3,
      "username": "client_en_attente1",
      "email": "attente1@example.com",
      "role": "CLIENT",
      "is_active": false
    },
    {
      "id": 4,
      "username": "client_en_attente2",
      "email": "attente2@example.com",
      "role": "CLIENT",
      "is_active": false
    }
  ]
}
```
- **403 Forbidden** - Permission refusée

---

### POST `/users/{user_id}/validate/`
**Validation ou rejet d'un compte client**

#### Permissions
- Authentification requise (IsAuthenticated)
- Rôle Agent ou Superutilisateur requis

#### Paramètres d'URL
- `user_id` : ID de l'utilisateur à valider/rejeter (requis)

#### Paramètres du corps de requête
```json
{
  "is_active": true  // true pour valider, false pour rejeter
}
```

#### Contraintes
- Seuls les comptes avec le rôle CLIENT peuvent être validés

#### Réponses
- **200 OK** - Validation/rejet réussi
```json
{
  "message": "Compte validé avec succès",
  "user": {
    "id": 3,
    "username": "client_valide",
    "email": "client@example.com",
    "role": "CLIENT",
    "is_active": true
  }
}
```
- **400 Bad Request** - Erreur de validation ou utilisateur non-client
- **403 Forbidden** - Permission refusée
- **404 Not Found** - Utilisateur introuvable

---

## 🛡️ Administration (Superutilisateur uniquement)

### POST `/create-agent/`
**Création d'un compte agent**

#### Permissions
- Authentification requise (IsAuthenticated)
- Rôle Superutilisateur requis

#### Paramètres du corps de requête
```json
{
  "username": "string",      // Nom d'utilisateur (requis)
  "email": "string",         // Adresse email (requis)
  "password": "string",      // Mot de passe (requis)
  "first_name": "string",    // Prénom (optionnel)
  "last_name": "string"      // Nom de famille (optionnel)
}
```

#### Notes
- Le rôle est automatiquement défini sur AGENT
- Le compte agent est automatiquement activé

#### Réponses
- **201 Created** - Agent créé avec succès
```json
{
  "message": "Agent créé avec succès",
  "user": {
    "id": 5,
    "username": "nouvel_agent",
    "email": "agent@example.com",
    "role": "AGENT",
    "is_active": true
  }
}
```
- **400 Bad Request** - Erreur de validation
- **403 Forbidden** - Permission refusée (non-superutilisateur)

---

## 📋 Codes de Statut HTTP

| Code | Description |
|------|-------------|
| 200  | Succès - Requête traitée avec succès |
| 201  | Créé - Ressource créée avec succès |
| 400  | Requête incorrecte - Erreur de validation |
| 403  | Interdit - Permissions insuffisantes |
| 404  | Non trouvé - Ressource introuvable |

---

## 🔑 Système de Rôles

### CLIENT
- Peut s'inscrire et se connecter
- Peut consulter et modifier son profil
- Compte nécessite une validation par un Agent/Superutilisateur

### AGENT
- Toutes les permissions des clients
- Peut consulter la liste des clients
- Peut valider/rejeter les comptes clients
- Peut voir les comptes en attente de validation

### SUPERUSER
- Toutes les permissions des agents
- Peut consulter tous les utilisateurs (tous rôles)
- Peut créer des comptes agents
- Accès administratif complet

---

## 📝 Notes Importantes

1. **Activation des comptes** : Les nouveaux comptes clients sont créés avec `is_active=false` et nécessitent une validation.

2. **Sécurité** : Toutes les vues sensibles nécessitent une authentification et vérifient les permissions appropriées.

3. **Filtrage des données** : Les agents ne peuvent voir que les clients, tandis que les superutilisateurs ont accès à tous les utilisateurs.

4. **Validation** : Seuls les comptes avec le rôle CLIENT peuvent être validés via l'endpoint de validation.