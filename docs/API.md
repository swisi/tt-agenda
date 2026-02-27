# API (v2)

## Zweck

Diese Datei beschreibt die HTTP-Schnittstellen der v2-Anwendung.

## Verfügbare Endpunkte (aktueller Stand)

### Health

- `GET /health/live`
- `GET /health/ready`

### Auth

- `POST /auth/login`
  - Request: `{ "username": "...", "password": "..." }`
  - Response: `{ "ok": true, "username": "...", "role": "admin|coach" }`

### Position Groups

- `GET /api/v1/position-groups`
- `POST /api/v1/position-groups`
  - Request: `{ "name": "Line", "position_codes": ["OL", "DL"] }`

### Templates

- `GET /api/v1/templates`
- `POST /api/v1/templates`
- `PATCH /api/v1/templates/{template_id}`
- `POST /api/v1/templates/{template_id}/overrides`

### Ad-hoc Einheiten

- `POST /api/v1/instances/adhoc`

### Schedule (berechnet)

- `GET /api/v1/schedule?from=YYYY-MM-DD&to=YYYY-MM-DD`
  - Liefert template-basierte Einheiten inkl. Overrides und ad-hoc Einheiten
  - Endzeit wird aus `Startzeit + Aktivitätsdauer` berechnet

### WebSocket Live Updates (`/ws/live`)

- Verbindung: `ws://<host>/ws/live` (oder `wss://` bei TLS). Optionaler Auth-Token: Query `?token=...` oder Header `x-ws-token: ...`.
- Beim Verbindungsaufbau sendet der Server eine initiale Snapshot-Nachricht:

```json
{"ok": true, "items": [ /* array of schedule items like in /api/v1/schedule */ ], "count": N}
```

- Danach sendet der Server nur noch Diffs, wenn sich der heutige Schedule ändert. Diff-Nachrichten haben das Format:

```json
{
  "ok": true,
  "type": "diff",
  "diff": {
    "added": [ /* schedule items added */ ],
    "removed": [ /* keys (date|start_time|name|source) of removed items */ ],
    "updated": [ /* schedule items with updated content */ ]
  },
  "count": 42
}
```

Clients should apply `added` and `updated` entries and remove any item whose composite key (`date|start_time|name|source`) appears in `removed`.

## Versionierung

- Aktuell: `/api/v1/...`
