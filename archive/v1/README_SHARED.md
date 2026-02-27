# TT-Shared Integration

## Über TT-Shared

Das [tt-shared](https://github.com/swisi/tt-shared) Repository enthält ein gemeinsames Design-System für Tigers Microservices mit:

- 🎨 Tailwind CSS Dark/Light Mode
- 📱 Responsive Navigation mit Tigers Branding
- 🌙 Theme Toggle mit LocalStorage
- 📦 Gemeinsame CSS & JavaScript Komponenten

## Installation

Das Submodul wurde bereits hinzugefügt im Verzeichnis `shared/`:

```bash
# Bei Bedarf Submodul aktualisieren
git submodule update --init --recursive
```

## Verwendung

### Option 1: Shared Base Template verwenden

Nutze das gemeinsame base.html aus tt-shared:

```html
{% extends "base.html" %}

{% block content %}
  <h1>Dein Content</h1>
{% endblock %}
```

Die Flask-App ist bereits so konfiguriert, dass sie zuerst im lokalen `templates/` Ordner sucht und dann in `shared/templates/`.

### Option 2: Nur Shared Styles verwenden

In deinem bestehenden Template:

```html
<link rel="stylesheet" href="{{ url_for('shared_static', filename='css/globals.css') }}">
<script src="{{ url_for('shared_static', filename='js/theme-toggle.js') }}"></script>
```

### Verfügbare Shared Assets

- **CSS**: `/shared/css/globals.css` - Globale Styles mit Tailwind-Klassen
- **JavaScript**: `/shared/js/theme-toggle.js` - Dark/Light Mode Toggle

### CSS Klassen aus TT-Shared

```html
<!-- Buttons -->
<button class="btn btn-primary">Primary</button>
<button class="btn btn-secondary">Secondary</button>
<button class="btn btn-danger">Danger</button>
<button class="btn btn-success">Success</button>

<!-- Badges -->
<span class="badge badge-primary">Primary</span>
<span class="badge badge-success">Success</span>
<span class="badge badge-warning">Warning</span>
<span class="badge badge-danger">Danger</span>

<!-- Cards -->
<div class="card p-6">
  <h2>Card Title</h2>
  <p>Card content</p>
</div>

<!-- Forms -->
<div class="form-group">
  <label>Label</label>
  <input type="text" placeholder="Placeholder">
</div>
```

## Updates

Um die neueste Version von tt-shared zu holen:

```bash
cd shared
git pull origin main
cd ..
git add shared
git commit -m "Update tt-shared submodule"
```

## Navigation und Branding

Das shared base.html enthält:
- Tigers Logo mit Trophäe Icon
- Responsive Navigation
- Dark Mode Toggle
- User Authentication UI (Login/Logout)

Um die Navigation anzupassen, kannst du das lokale Template überschreiben oder Blöcke ersetzen.
