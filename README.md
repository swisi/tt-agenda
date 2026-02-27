# Trainingsverwaltung - Thun Tigers

Eine moderne, benutzerfreundliche Web-Anwendung zur Verwaltung von Trainings, Aktivitäten und Live-Übersichten für Sportvereine.

## Features

### 🎯 Kernfunktionalität

- **Trainings-Management**: Erstellen, bearbeiten und duplizieren von wiederkehrenden Trainings-Templates
- **Einmalige Trainings**: Verwaltung von speziellen, einzelnen Trainingsevent
- **Angepasste Termine**: Individuelle Anpassungen von Template-Trainings
- **Aktivitätstypen**: Konfigurierbare Aktivitätskategorien mit Farbcodierung

### 🎨 Design & UX

- **Modernes Design**: Glassmorphism mit Indigo-Farbschema
- **Dark Mode**: Vollständiger Dark Mode Support
- **Responsive Layout**: Optimiert für alle Bildschirmgrößen
- **HTMX Integration**: Flüssige, progressive Enhancement ohne SPA-Komplexität

### ⚡ Live-View

- **Echtzeit-Übersicht**: Aktuelle Trainings mit Live-Indikatoren
- **Positions-Filter**: Filterung nach Spielerpositionen
- **Zeitanzeige**: Countdown-Timer und aktuelle Uhrzeit
- **Status-Anzeige**: Visueller Status für aktuelle, nächste und abgelaufene Aktivitäten

### 🔐 Administration

- **Admin-Panel**: Zentrale Verwaltung aller Trainings
- **Benutzer-Management**: Admin und User Rollen
- **Backup & Restore**: Datenbank-Sicherung und Wiederherstellung
- **Aktivitäts-Verwaltung**: Konfiguration von Aktivitätstypen und deren Darstellung

## Installation

### Anforderungen

- Python 3.12+
- pip oder poetry
- SQLite (standardmäßig enthalten)

### Schritt 1: Repository klonen

```bash
git clone https://github.com/yourusername/tt-agenda.git
cd tt-agenda
```

### Schritt 2: Virtual Environment erstellen

```bash
python3.12 -m venv venv
source venv/bin/activate  # Auf macOS/Linux
# oder
venv\Scripts\activate  # Auf Windows
```

### Schritt 3: Dependencies installieren

```bash
pip install -r requirements.txt
```

### Schritt 4: Umgebungsvariablen konfigurieren

```bash
cp .env.example .env
```

Bearbeite `.env` mit deinen Einstellungen:

```env
SECRET_KEY=dein-geheimnis-schlüssel
LOG_LEVEL=DEBUG
AUTO_CREATE_DB=true
CREATE_DEFAULT_USERS=true
```

### Schritt 5: Anwendung starten

```bash
python run.py
```

Die App läuft dann unter: **<http://127.0.0.1:5000>**

## Konfiguration

### Umgebungsvariablen (.env)

| Variable | Beschreibung | Standard |
| ---------- | ------------- | ---------- |
| `SECRET_KEY` | Flask Session-Schlüssel | Erforderlich |
| `LOG_LEVEL` | Logging-Level (DEBUG/INFO/WARNING) | DEBUG |
| `AUTO_CREATE_DB` | Datenbank automatisch erstellen | true |
| `CREATE_DEFAULT_USERS` | Standard-Benutzer anlegen | true |
| `WEBHOOK_ENABLED` | Webhooks aktivieren | false |
| `WEBHOOK_URL` | Webhook-Ziel-URL | Optional |

### Standardbenutzer

Wenn `CREATE_DEFAULT_USERS=true`, werden folgende Benutzer erstellt:

- **Admin**: `admin` / `admin123`
- **User**: `user` / `user123`

## Verwendung

### 📊 Hauptseite (Übersicht)

- Aktuelle und kommende Trainings anzeigen
- Trainings-Status visuell darstellen
- Navigation zu Live-View und Admin

### 🎬 Live-View

- Klick auf "Live Training" in der Navbar
- Echtzeit-Trainingsverlauf mit Aktivitäten
- Positions-Filter zum Filtern nach Spielergruppen
- Countdown-Timer für aktuelle Aktivität

### ⚙️ Administration

- Klick auf "Administration" in der Navbar
- **Trainings verwalten**: Alle Trainings in einer übersichtlichen Tabelle
  - Filter nach Name und Typ
  - Bearbeiten, Duplizieren, Löschen
- **Aktivitätstypen**: Konfigurieren von Aktivitäten-Kategorien
- **Backup & Restore**: Datenbank sichern und wiederherstellen

## Projektstruktur

``` txt
tt-agenda/
├── app/
│   ├── __init__.py
│   ├── config.py              # Flask-Konfiguration
│   ├── models.py              # Datenbank-Modelle
│   ├── extensions.py          # Flask-Erweiterungen (DB, etc.)
│   ├── utils.py               # Hilfsfunktionen
│   ├── activity_colors.py     # Aktivitäts-Farbkonfiguration
│   ├── routes/
│   │   ├── main.py            # Haupt-Routen
│   │   ├── auth.py            # Authentifizierung
│   │   └── admin.py           # Admin-Routen
│   ├── templates/             # Jinja2-Templates
│   ├── static/
│   │   └── css/
│   │       └── style.css      # Hauptstylesheet
│   └── instance/              # Datenbankdatei
├── tests/                     # Unit Tests
├── run.py                     # Einstiegspunkt
├── requirements.txt           # Dependencies
└── README.md
```

## Technologie-Stack

### Backend

- **Flask 3.0.0**: Lightweight Web Framework
- **SQLAlchemy 3.1.1**: ORM für Datenbankoperationen
- **python-dotenv 1.0.0**: Umgebungsvariablen-Management

### Frontend

- **Bootstrap 5.3.0**: CSS Framework
- **HTMX 1.9.12**: Progressive Enhancement
- **Bootstrap Icons 1.10.0**: Icon Library
- **Inter Font**: Moderne Systemschrift

### Entwicklung

- **Gunicorn 21.2.0**: WSGI Application Server
- **Pytest 8.0.0**: Testing Framework

## API-Endpunkte

### Public

- `GET /` - Startseite mit Trainings-Übersicht
- `GET /live` - Live-Training View
- `POST /auth/login` - Login
- `GET /auth/logout` - Logout

### Admin (erfordert Admin-Rolle)

- `GET /admin/trainings` - Trainings-Verwaltung
- `GET /admin/trainings/partial` - HTMX Filter-Partial
- `POST /training/<id>/copy` - Training duplizieren
- `POST /training/<id>/delete` - Training löschen
- `GET /admin/activity-types` - Aktivitätstypen-Verwaltung
- `GET /admin/backup` - Backup & Restore

## Entwicklungsumgebung

### Tests ausführen

```bash
pytest
```

### Debug-Modus

Ist standardmäßig bei `LOG_LEVEL=DEBUG` aktiviert:

```bash
python run.py
```

### Neues Feature hinzufügen

1. **Route erstellen** in `app/routes/`:

```python
@bp.route('/new-feature')
def new_feature():
    return render_template('new_feature.html')
```

1. **Template erstellen** in `app/templates/`:

```html
{% extends "base.html" %}
{% block content %}
<!-- Inhalt hier -->
{% endblock %}
```

1. **Datenbankmodell** (falls nötig) in `app/models.py`:

```python
class NewModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Fields...
```

## Browser-Unterstützung

- Chrome/Chromium 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Performance-Optimierungen

- **HTMX**: Minimale Bandbreite durch HTML-Austausch statt JSON
- **CSS Custom Properties**: Dynamische Theme-Anpassung ohne Page Reload
- **Lazy Loading**: Bilder und Ressourcen werden bedarfsgerecht geladen
- **Dark Mode**: Reduziert Augenlast und Energieverbrauch

## Sicherheit

- **CSRF-Protection**: Alle Forms mit CSRF-Token
- **Password Hashing**: Sichere Password-Speicherung mit Werkzeug
- **Session Management**: Sichere Session-Verwaltung mit Flask
- **SQL Injection Protection**: Parametrisierte Queries mit SQLAlchemy

## Lizenz

Dieses Projekt ist lizenziert unter der MIT-Lizenz.

## Kontakt & Support

Bei Fragen oder Problemen bitte ein Issue erstellen oder den Administrator kontaktieren.

---

**Version**: 0.2.0  
**Letzte Aktualisierung**: Januar 2026  
**Entwickler**: Trainingsverwaltungs-Team
