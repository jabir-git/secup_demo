# SecUp API Guide

## Base Info
- Base URL (local): `http://localhost:8000`
- Health endpoint: `GET /health`
- Auth scheme: `Authorization: Bearer <access_token>`
- API prefix: `/api`
- OpenAPI docs: `http://localhost:8000/docs`
- Trailing slashes are **not** redirected — use exact paths as documented

## Startup Seeding
On app startup, database seeding runs automatically when tables are empty.

- Triggered from `main.py` lifespan
- Seed source: `seed.py`
- Includes fixed mobile test users

## Mobile Test Users
Use these accounts to login from mobile:

- `agent.alpha` / `AgentAlpha@2026!`
- `agent.bravo` / `AgentBravo@2026!`
- `supervisor.charlie` / `SupervisorCharlie@2026!`

## Authentication

### `POST /api/auth/register`
Create a user account.

Request body:
```json
{
  "username": "new.agent",
  "email": "new.agent@secup.gn",
  "password": "StrongPass@2026"
}
```

Response:
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user_id": 1,
  "username": "new.agent",
  "email": "new.agent@secup.gn"
}
```

### `POST /api/auth/login`
Login with `email` + `password`. **Rate limited to 10 requests/minute per IP.**

```json
{
  "email": "agent.alpha@secup.gn",
  "password": "AgentAlpha@2026!"
}
```

Returns same shape as register response (includes `expires_in`).

### `POST /api/auth/refresh`
Refresh tokens.

```json
{
  "refresh_token": "..."
}
```

### `POST /api/auth/logout`
Requires access token. Blacklists current token.

### `GET /api/auth/me`
Requires access token. Returns user profile.

## Vehicles
All endpoints require bearer token.

Driver info is embedded directly on the vehicle record (no separate driver resource).

Deleted vehicles are soft-deleted (`deleted_at` is set) and excluded from all responses.

### `GET /api/vehicles?status=<value>&event_type=<value>&cursor=<id>&limit=20`
List vehicles with optional filters and keyset cursor pagination.

- `status`: `normal` | `wanted` | `stolen` | `suspicious` (omit for all)
- `event_type`: `alert` | `intervention` (omit for all)
- `cursor`: last seen `id` — returns items with `id < cursor`
- `limit`: default `20`

Response shape:
```json
{
  "items": [],
  "limit": 20,
  "next_cursor": null,
  "has_more": false
}
```

### `POST /api/vehicles`
```json
{
  "license_plate": "GY-1234-AB",
  "vehicle_info": "Toyota - SUV - 2021 - Noir",
  "notes": "No visible damage",
  "status": "normal",
  "event_type": "intervention",
  "driver_full_name": "Mamadou Diallo",
  "driver_license_number": "123456789012",
  "driver_phone": "+224620000001"
}
```

`status` values: `normal` | `wanted` | `stolen` | `suspicious`

`event_type` values: `alert` | `intervention` | `null`

Returns `400` if `driver_license_number` already exists on a non-deleted vehicle.

### `GET /api/vehicles/search?q=<text>`
Search by license plate, driver name, or driver license number. Returns up to 10 results.

### `GET /api/vehicles/by-license/{license_number}`
Get vehicle by driver license number.

### `GET /api/vehicles/{vehicle_id}`
Get one vehicle.

### `PUT /api/vehicles/{vehicle_id}`
Full or partial update. Accepts any fields from the create payload.

### `PATCH /api/vehicles/{vehicle_id}/status?status=<value>`
Set vehicle status directly.

### `PATCH /api/vehicles/batch-status`
Update the status of multiple vehicles in one request.

Request body:
```json
{
  "ids": [1, 2, 3],
  "status": "wanted"
}
```

Returns the list of updated vehicle objects. IDs that don't exist or are soft-deleted are silently skipped.

### `DELETE /api/vehicles/{vehicle_id}`
Soft delete — sets `deleted_at` timestamp. Vehicle is excluded from all subsequent queries.

## Common Error Responses
- `400`: bad request (validation/business rule)
- `401`: unauthorized or invalid token
- `404`: resource not found
- `429`: rate limit exceeded (login endpoint)

Typical format:
```json
{
  "detail": "Error message"
}
```

## Quick cURL Login Example
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"agent.alpha@secup.gn","password":"AgentAlpha@2026!"}'
```
