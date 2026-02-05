# TT-Shared Integration - Quick Start

## ✅ Installation abgeschlossen

Das tt-shared Submodul wurde erfolgreich eingebunden unter `shared/`.

## 🧪 Testen

1. **Anwendung starten:**
   ```bash
   python run.py
   ```

2. **Beispiel-Seite aufrufen:**
   - Öffne im Browser: `http://localhost:5000/shared-example`
   - Diese Seite zeigt das TT-Shared Design-System in Aktion

3. **Features testen:**
   - Dark/Light Mode Toggle (oben rechts)
   - Responsive Navigation
   - Shared CSS Klassen (Buttons, Badges, Cards, Forms)

## 📝 Verwendung in bestehenden Templates

### Option A: Shared base.html verwenden

Erstelle ein neues Template oder passe ein bestehendes an:

```html
{% extends "base.html" %}

{% block content %}
  <!-- Dein Content hier -->
{% endblock %}
```

### Option B: Nur Shared Styles nutzen

In deinem Template Head:

```html
<link rel="stylesheet" href="{{ url_for('shared_static', filename='css/globals.css') }}">
<script src="{{ url_for('shared_static', filename='js/theme-toggle.js') }}"></script>
```

## 🔄 Updates holen

```bash
git submodule update --remote shared
git add shared
git commit -m "Update tt-shared to latest version"
```

## 📚 Weitere Informationen

Siehe [README_SHARED.md](README_SHARED.md) für vollständige Dokumentation.
