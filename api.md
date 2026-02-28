# SecUp API Documentation

API REST pour l'application mobile de gestion des infractions routières.

---

## Base URL

```
http://localhost:8000
```

---

## Authentification

Toutes les routes protégées nécessitent un header :

```
Authorization: Bearer <access_token>
```

---

## Rôles Utilisateurs

| Rôle         | Permissions                                       |
| ------------ | ------------------------------------------------- |
| `agent`      | CRUD basique sur ses propres ressources           |
| `supervisor` | + Libérer véhicules, marquer recherché, supprimer |
| `admin`      | Accès complet                                     |

---

## 🔐 Auth (`/api/auth`)

### POST `/api/auth/register`

Créer un nouveau compte.

**Request:**

```json
{
  "username": "string (3-50 chars)",
  "email": "string (email valide)",
  "password": "string (min 8 chars)"
}
```

**Response:** `201 Created`

```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer",
  "expires_in": 3600,
  "user_id": 1,
  "username": "string",
  "email": "string"
}
```

---

### POST `/api/auth/login`

Se connecter avec username ou email.

**Request:**

```json
{
  "username": "string (optionnel)",
  "email": "string (optionnel)",
  "password": "string"
}
```

**Response:** `200 OK` — Même structure que register

---

### POST `/api/auth/refresh`

Renouveler le token d'accès.

**Request:**

```json
{
  "refresh_token": "string"
}
```

**Response:** `200 OK` — Même structure que login

---

### POST `/api/auth/logout`

Se déconnecter.

**Response:** `200 OK`

```json
{
  "message": "Logged out successfully"
}
```

---

### GET `/api/auth/me` 🔒

Récupérer le profil de l'utilisateur connecté.

**Response:** `200 OK`

```json
{
  "id": 1,
  "username": "string",
  "email": "string",
  "role": "agent|supervisor|admin",
  "badge_number": "string|null",
  "phone": "string|null",
  "department": "string|null",
  "is_active": true,
  "created_at": "2026-01-11T10:00:00Z"
}
```

---

### PUT `/api/auth/me` 🔒

Mettre à jour son profil.

**Request:**

```json
{
  "badge_number": "string (optionnel)",
  "phone": "string (optionnel)",
  "department": "string (optionnel)"
}
```

**Response:** `200 OK` — Même structure que GET /me

---

## 🚗 Véhicules (`/api/vehicles`)

### POST `/api/vehicles/` 🔒

Créer un véhicule.

**Request:**

```json
{
  "license_plate": "RC-1234-AB",
  "make": "Toyota",
  "model": "Corolla",
  "year": 2020,
  "color": "Blanc",
  "vin": "string (optionnel)",
  "vehicle_type": "voiture|moto|camion|bus|taxi",
  "driver_id": 1,
  "is_wanted": false
}
```

**Response:** `201 Created`

```json
{
  "id": 1,
  "license_plate": "RC-1234-AB",
  "make": "Toyota",
  "model": "Corolla",
  "year": 2020,
  "color": "Blanc",
  "vin": "string|null",
  "vehicle_type": "voiture",
  "status": "active|seized|released",
  "seizure_reason": "string|null",
  "seizure_date": "datetime|null",
  "seizure_location": "string|null",
  "release_date": "datetime|null",
  "driver_id": 1,
  "seized_by_user_id": null,
  "is_wanted": false,
  "is_deleted": false,
  "created_at": "2026-01-11T10:00:00Z",
  "updated_at": "2026-01-11T10:00:00Z"
}
```

---

### GET `/api/vehicles/search?plate=RC-1234` 🔒

Recherche rapide par plaque (partielle).

**Response:** `200 OK` — Liste de véhicules (max 10)

---

### GET `/api/vehicles/wanted` 🔒

Liste des véhicules recherchés.

**Response:** `200 OK` — Liste de véhicules où `is_wanted=true`

---

### GET `/api/vehicles/{id}` 🔒

Récupérer un véhicule par ID.

**Response:** `200 OK` — Objet véhicule

---

### PUT `/api/vehicles/{id}` 🔒

Modifier un véhicule.

**Request:** Champs optionnels de création

**Response:** `200 OK` — Véhicule mis à jour

---

### DELETE `/api/vehicles/{id}` 🔒

Supprimer un véhicule (soft delete).

**Response:** `204 No Content`

---

### POST `/api/vehicles/{id}/seize` 🔒

**Saisir un véhicule.**

**Request:**

```json
{
  "seizure_reason": "Défaut d'assurance",
  "seizure_location": "Carrefour Cosa, Conakry"
}
```

**Response:** `200 OK` — Véhicule avec `status: "seized"`

---

### POST `/api/vehicles/{id}/release` 🔒 (supervisor/admin)

**Libérer un véhicule saisi.**

**Response:** `200 OK` — Véhicule avec `status: "released"`

---

### PATCH `/api/vehicles/{id}/wanted?is_wanted=true` 🔒 (supervisor/admin)

**Marquer comme recherché.**

**Response:** `200 OK` — Véhicule mis à jour

---

## 👤 Conducteurs (`/api/drivers`)

### POST `/api/drivers/` 🔒

Créer un conducteur.

**Request:**

```json
{
  "first_name": "Mamadou",
  "last_name": "Diallo",
  "date_of_birth": "1990-05-15",
  "address": "Quartier Madina",
  "city": "Conakry",
  "phone": "+224 620 00 00 00",
  "license_number": "GN-12345678",
  "license_category": "B",
  "license_expiry": "2028-12-31",
  "national_id": "CNI-1234567890"
}
```

**Response:** `201 Created`

```json
{
  "id": 1,
  "first_name": "Mamadou",
  "last_name": "Diallo",
  "date_of_birth": "1990-05-15T00:00:00Z",
  "address": "Quartier Madina",
  "city": "Conakry",
  "phone": "+224 620 00 00 00",
  "license_number": "GN-12345678",
  "license_category": "B",
  "license_expiry": "2028-12-31T00:00:00Z",
  "national_id": "CNI-1234567890",
  "is_deleted": false,
  "created_at": "2026-01-11T10:00:00Z",
  "updated_at": "2026-01-11T10:00:00Z"
}
```

---

### GET `/api/drivers/search?q=Diallo` 🔒

Recherche par nom, prénom, permis ou CNI (max 10).

**Response:** `200 OK` — Liste de conducteurs

---

### GET `/api/drivers/by-license/{license_number}` 🔒

Récupérer par numéro de permis.

**Response:** `200 OK` — Objet conducteur

---

### GET `/api/drivers/{id}` 🔒

Récupérer par ID.

**Response:** `200 OK` — Objet conducteur

---

### PUT `/api/drivers/{id}` 🔒

Modifier un conducteur.

**Response:** `200 OK` — Conducteur mis à jour

---

### DELETE `/api/drivers/{id}` 🔒 (supervisor/admin)

Supprimer un conducteur.

**Response:** `204 No Content`

---

## 🚨 Alertes (`/api/alerts`)

### GET `/api/alerts/?skip=0&limit=10&license_plate=RC-1234` 🔒

Liste des alertes de l'utilisateur.

**Response:** `200 OK`

```json
{
  "data": [
    {
      "id": 1,
      "title": "string",
      "description": "string",
      "status": "pending|active|resolved",
      "license_plate": "string|null",
      "is_resolved": false,
      "is_deleted": false,
      "user_id": 1,
      "created_at": "datetime",
      "updated_at": "datetime"
    }
  ],
  "total": 20,
  "skip": 0,
  "limit": 10,
  "pages": 2
}
```

---

### POST `/api/alerts/` 🔒

Créer une alerte.

**Request:**

```json
{
  "title": "Véhicule suspect",
  "description": "Toyota blanche stationnée illégalement",
  "status": "pending",
  "license_plate": "RC-1234-AB"
}
```

---

### PATCH `/api/alerts/{id}` 🔒

Modifier une alerte.

---

### DELETE `/api/alerts/{id}` 🔒

Supprimer une alerte.

**Response:** `{"message": "alert deleted"}`

---

## 📋 Interventions (`/api/interventions`)

### GET `/api/interventions/?cursor=123&limit=10` 🔒

Liste des interventions. Pagination par curseur avec `cursor` (id du dernier element).

**Response:** `200 OK`

```json
{
  "items": [
    {
      "id": 1,
      "title": "Contrôle routier",
      "description": "string",
      "license_plate": "string|null",
      "is_deleted": false,
      "user_id": 1,
      "created_at": "datetime",
      "updated_at": "datetime"
    }
  ],
  "limit": 10,
  "next_cursor": 110,
  "has_more": true
}
```

---

### POST `/api/interventions/` 🔒

Créer une intervention.

**Request:**

```json
{
  "title": "Excès de vitesse",
  "description": "Véhicule roulant à 120km/h en zone 50",
  "license_plate": "RC-5678-CD"
}
```

---

### PATCH `/api/interventions/{id}` 🔒

Modifier une intervention.

---

### DELETE `/api/interventions/{id}` 🔒

Supprimer une intervention.

**Response:** `{"message": "intervention deleted"}`

---

## ❤️ Health Check

### GET `/health`

```json
{
  "status": "ok"
}
```

---

## Codes d'erreur

| Code  | Description                     |
| ----- | ------------------------------- |
| `200` | Succès                          |
| `201` | Créé                            |
| `204` | Supprimé (pas de contenu)       |
| `400` | Requête invalide                |
| `401` | Non authentifié                 |
| `403` | Accès refusé (rôle insuffisant) |
| `404` | Ressource non trouvée           |

**Format d'erreur:**

```json
{
  "detail": "Message d'erreur"
}
```

---

## Comptes de test

| Rôle        | Username     | Password       |
| ----------- | ------------ | -------------- |
| Admin       | `admin`      | `Admin@2026!`  |
| Superviseur | `supervisor` | `Super@2026!`  |
| Agent       | `agent1`     | `Agent1@2026!` |

---

## Notes

- 🔒 = Route protégée (nécessite Bearer token)
- Timestamps en format ISO 8601
- Soft delete : les éléments supprimés ont `is_deleted: true`
- CORS activé pour toutes les origines
