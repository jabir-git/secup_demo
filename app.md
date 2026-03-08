# SecUp Mobile App — Build Notes

Build a mobile app for police traffic control agents to interact with the SecUp backend.

## Key Notes
- Plate search supports manual typing and plate scanning (camera OCR)
- Driver and vehicle data are merged: a vehicle record carries the driver's info directly
- `event_type` on the vehicle record indicates the last event context (`alert` or `intervention`)
- All list endpoints use keyset (cursor) pagination — pass `next_cursor` as `cursor` in the next request
- Deleted vehicles are excluded server-side; no client-side filtering needed
- Login is rate-limited (10 req/min per IP) — surface a friendly error on `429`

## Data Model

### Vehicle (with embedded driver)
| Field | Type | Notes |
|---|---|---|
| `id` | int | Primary key |
| `license_plate` | string | Indexed, searchable |
| `vehicle_info` | string? | Make, type, year, color |
| `status` | string | `normal` \| `wanted` \| `stolen` \| `suspicious` |
| `event_type` | string? | `alert` \| `intervention` \| null |
| `driver_full_name` | string? | Embedded driver name |
| `driver_license_number` | string? | Unique, searchable |
| `driver_phone` | string? | Driver contact |
| `notes` | string? | Free text |
| `created_at` | datetime | ISO 8601 with timezone |
| `updated_at` | datetime | ISO 8601 with timezone |

## Core Workflows

### Plate Lookup
1. Agent scans or types a plate
2. `GET /api/vehicles/search?q=<plate>` — returns matching vehicles with embedded driver info
3. Display vehicle status, driver name, license number

### Driver Lookup
- `GET /api/vehicles/search?q=<name or license_number>` — same search endpoint covers driver fields

### Tag Event Type on Vehicle
- `PUT /api/vehicles/{id}` with `event_type: "alert"` or `event_type: "intervention"`

### Mark Vehicle Status
- `PATCH /api/vehicles/{id}/status?status=wanted` — flag a single vehicle

### Bulk Status Update (Supervisor)
- `PATCH /api/vehicles/batch-status` — update multiple vehicles at once
- Body: `{ "ids": [1, 2, 3], "status": "wanted" }`

### Paginated Vehicle List
- `GET /api/vehicles?event_type=alert&limit=20` — first page
- On scroll, pass `cursor=<next_cursor>` from the previous response
- Stop when `has_more` is `false`
