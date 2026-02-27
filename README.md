# TT-Agenda (Refactoring v2)

Dieses Repository wurde für ein vollständiges Refactoring neu gestartet.

## Status

- Legacy-Code liegt im Archiv: `archive/v1/`
- Aktive Entwicklungsbasis wird neu aufgebaut
- Diese Doku ist die zentrale Referenz für v2

## Zielbild v2

- Klare modulare Architektur
- Saubere Trennung von Domain, Application, Infrastructure, UI
- Testbare Kernlogik
- Reproduzierbares Setup (lokal/CI/Deployment)
- Dokumentierte APIs und Betriebsprozesse

## Dokumentation

- [Requirements](docs/REQUIREMENTS.md)
- [Architektur](docs/ARCHITEKTUR.md)
- [Setup](docs/SETUP.md)
- [Betrieb](docs/BETRIEB.md)
- [API](docs/API.md)
- [Contribution](docs/CONTRIBUTING.md)
- [Refactoring-Plan](docs/REFACTORING_PLAN.md)

## v2 Struktur (aktuell)

```text
src/
 tt_agenda_v2/
  database.py
  models.py
  services/
  interface/http/
tests/
run.py
requirements.txt
```

- Backend: FastAPI
- Persistenz: plain SQLAlchemy (ohne Flask-SQLAlchemy)

## Schnellstart

```powershell
py -3.12 -m venv .venv
& .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pytest -q
python run.py
# öffne http://127.0.0.1:5000/ für die Live-Ansicht oder /docs für die API-Doku
```

## UI / Live-Ansicht

- Root (`/`): Server-gerenderte Live-Ansicht mit Countdown-Timer und Hervorhebung der aktuell aktiven Aktivität.
- Trainingsverwaltung:
  - `GET /templates` — Liste der Trainingsvorlagen
  - `GET /templates/{id}/edit` — einfache Bearbeitungsseite (POST zum Speichern)
- Statische Assets liegen unter `/static/` (CSS/JS). Die Live-Ansicht polled `/api/v1/schedule` regelmäßig und zeigt die nächste/aktive Aktivität an; bei 10 Sekunden verbleibend wird eine akustische Warnung ausgelöst.
- Formular-POSTs werden serverseitig verarbeitet; für produktive Deployments empfiehlt es sich, `python-multipart` zu installieren, damit Starlette/FastAPI native Form-Parsing nutzen kann.

### WebSocket-Authentifizierung (optional)

- Die WebSocket-Endpunkte unterstützen eine einfache, optional aktivierbare Token-Prüfung.
- Konfiguration: Setze `WS_AUTH_TOKEN` in der App-Konfiguration oder im Config-Klassen-Objekt, das du an `create_app()` übergibst.
- Clients müssen den Token entweder als Query-Parameter `?token=...` oder als Header `x-ws-token: ...` mitsenden. Bei fehlendem/inkorrektem Token wird die Verbindung mit Close-Code 1008 abgewiesen.

Beispiel (Query-Parameter): `/ws/live?token=mein-geheimnis`
Beispiel (Header): `x-ws-token: mein-geheimnis`

### Deployment / Environment Beispiele für `WS_AUTH_TOKEN`

- Lokales Starten (PowerShell):

```powershell
$env:WS_AUTH_TOKEN = "mein-geheimnis"
python run.py
```

- Systemd service (Linux): setze EnvironmentFile oder `Environment=` in der Unit:

```yaml
[Service]
Environment="WS_AUTH_TOKEN=mein-geheimnis"
ExecStart=/usr/bin/python /srv/tt-agenda/run.py
```

- Docker Compose example:

```yaml
services:
  tt-agenda:
    image: your-image:latest
    environment:
      - WS_AUTH_TOKEN=mein-geheimnis
    ports:
      - "5000:5000"
```

- Kubernetes (Deployment env):

```yaml
env:
  - name: WS_AUTH_TOKEN
    value: "mein-geheimnis"
```

Client-Hinweis: Clients können den Token als Query-Parameter senden (`/ws/live?token=...`) oder als Header `x-ws-token: ...`.

## Hinweise zur Entwicklung

- Start: siehe Schnellstart oben.
- Tests: `python -m pytest -q` — es gibt Frontend-Smoketests, die die gerenderten Seiten und statischen Assets prüfen.

### Security Hinweise für `WS_AUTH_TOKEN`

- Vermeide Hardcoding: setze `WS_AUTH_TOKEN` über Umgebungsvariablen oder ein Secret-Manager (HashiCorp Vault, AWS Secrets Manager, Kubernetes Secrets).
- TLS: Verwende `wss://` in Produktion und betreibe den Server hinter einem TLS-Terminator oder Reverse-Proxy.
- Rotation & Länge: wähle lange, zufällige Tokens und rotiere sie regelmäßig. Plane einen einfachen Rollout/Revocation-Mechanismus.
- Logging & Limits: protokolliere abgewiesene Verbindungsversuche und ziehe Ratenbegrenzung / IP-Filter in Betracht.
- Least-privilege: beschränke Token-Zugriff auf notwendige Clients; nutze getrennte Tokens für interne Tools vs. öffentliche Clients.

Diese Maßnahmen reduzieren Risiko bei der einfachen Token-basierten Absicherung der WebSocket-Verbindung.

## Legacy

Der bisherige Stand ist ausschließlich zum Nachschlagen verfügbar:

- `archive/v1/`

Bitte dort keine aktiven Änderungen mehr vornehmen.

Hinweis: Frühere zusätzliche README-Dateien liegen nur noch im Archiv unter `archive/v1/`.
