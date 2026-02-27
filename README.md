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

## v2 Skelett (aktuell)

```text
src/
	tt_agenda_v2/
		domain/
		application/
		infrastructure/
		interface/http/
tests/
run.py
requirements.txt
```

## Schnellstart

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
python -m pytest -q
python run.py
```

## Legacy

Der bisherige Stand ist ausschließlich zum Nachschlagen verfügbar:

- `archive/v1/`

Bitte dort keine aktiven Änderungen mehr vornehmen.
