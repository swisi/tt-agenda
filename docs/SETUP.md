# Setup (v2)

## Voraussetzungen

- Python 3.12+
- Paketmanager: `pip`
- Optional: Docker

## Standard-Setup

```bash
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m pytest -q
python run.py
```

Die API läuft danach lokal auf `http://127.0.0.1:5000`.

## Konfiguration (Umgebungsvariablen)

- `SECRET_KEY`
- `DATABASE_URL`
- `AUTO_CREATE_DB` (`true`/`false`)
- `CREATE_DEFAULT_USERS` (`true`/`false`)
- `CREATE_DEFAULT_POSITIONS` (`true`/`false`)
- `DEFAULT_ADMIN_USERNAME` / `DEFAULT_ADMIN_PASSWORD`
- `DEFAULT_COACH_USERNAME` / `DEFAULT_COACH_PASSWORD`

Default-Logins:

- Admin: `admin` / `admin`
- Coach: `coach` / `coach`

## Backup-Test (v1 nach v2)

Der v2-Refactoring-Stand nutzt ein neues Datenmodell (Template/Override/Ad-hoc).
Ein v1-Backup kann deshalb nicht 1:1 ohne Mapping übernommen werden.

Empfohlener Testablauf:

1. v1-Backup separat bereithalten (`archive/v1/...`).
2. v2 mit eigener DB starten (z. B. `DATABASE_URL=sqlite:///tt_agenda_v2.db`).
3. Daten über die v2-API in Templates/Overrides überführen.
4. Ergebnisse über `GET /api/v1/schedule?from=YYYY-MM-DD&to=YYYY-MM-DD` validieren.

## Verifikation

```bash
python -m pytest tests/test_health.py tests/test_auth.py tests/test_schedule.py -q
```

## Hinweis

Ein automatisierter v1→v2 Importer ist noch nicht enthalten; die API für Templates, Overrides,
Positionsgruppen und Ad-hoc-Einheiten ist jedoch für den Migrationspfad bereits vorhanden.
