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

## Versionierung

- Aktuell: `/api/v1/...`
