# REQUIREMENTS – TT-Agenda v2

## 1. Ziel und Zweck

Dieses Dokument beschreibt die fachlichen und technischen Anforderungen für TT-Agenda v2.
Es dient als verbindliche Grundlage für Planung, Implementierung, Test und Abnahme.

## 2. Geltungsbereich (Scope)

**In Scope (v2 MVP):**

- Benutzeranmeldung mit Rollen (Admin/Coach)
- Verwaltung von Trainings (Anlegen, Bearbeiten, Löschen, Anzeigen)
- Verwaltung von Trainingseinheiten (Instanzen pro Datum)
- Verwaltung von Aktivitäten innerhalb einer Trainingseinheit
- Basis-Live-Ansicht für laufende Einheit
- Grundlegende Administrationsfunktionen

**Out of Scope (zunächst):**

- Mobile Native App
- Mehrmandantenfähigkeit
- Erweiterte externe Integrationen (über Basis-Webhooks hinaus)
- Vollständiges BI/Reporting

## 3. Stakeholder

- **Product Owner / Vereinsverantwortliche**: priorisieren Features
- **Trainerteam**: nutzen Trainings- und Live-Funktionalität
- **Administration**: verwaltet Stammdaten und Benutzer
- **Entwicklungsteam**: implementiert und betreibt v2

## 4. Produktübersicht

TT-Agenda v2 ist ein webbasiertes System zur Planung und Durchführung von Trainings.
Die Anwendung unterstützt den operativen Trainingsablauf von Planung bis Live-Durchführung.

## 5. Annahmen und Abhängigkeiten

- Deployment läuft in einer kontrollierten Serverumgebung.
- Benutzer greifen über aktuelle Browser zu.
- Zeitzone und Datumslogik sind konsistent konfiguriert.
- Altdaten aus `archive/v1/` werden bei Bedarf über definierte Migrationsschritte übernommen.

## 6. Funktionale Anforderungen

### 6.1 Authentifizierung & Autorisierung

- **FR-001** Das System muss Benutzer per Benutzername/Passwort anmelden können.
- **FR-002** Das System muss mindestens die Rollen `admin` und `coach` unterstützen.
- **FR-003** Das System muss geschützte Endpunkte für nicht angemeldete Benutzer blockieren.
- **FR-004** Das System muss rollenabhängige Berechtigungen erzwingen (Admin-Funktionen nur für Admin).

### 6.2 Trainingsverwaltung

- **FR-010** Admin kann Trainings anlegen.
- **FR-011** Admin kann Trainings bearbeiten.
- **FR-012** Admin kann Trainings löschen.
- **FR-013** Coaches können Trainingslisten anzeigen.
- **FR-014** Das System kann aktive/abgelaufene Trainings unterscheiden.

### 6.3 Trainingseinheiten (Instanzen)

- **FR-020** Das System muss Trainingseinheiten pro Datum verwalten.
- **FR-021** Admin kann Trainingseinheiten duplizieren.
- **FR-022** Das System verhindert doppelte Einheiten am selben Datum für dasselbe Training.
- **FR-023** Admin kann Trainingsvorgaben als **Template** definieren (mindestens: Zeitraum von/bis, Wochentag, Startzeit).
- **FR-024** Das System muss aus einem Template die zugehörigen Kalendereinträge im Zeitraum automatisch ableiten (z. B. alle Mittwoche im März); die Endzeit wird aus `Startzeit + Summe der Aktivitätsdauern` berechnet.
- **FR-025** Einzelne Termine, die einem Template entsprechen, müssen datumsspezifisch angepasst werden können (Override).
- **FR-026** Zur Redundanzvermeidung speichert das System für template-basierte Termine nur das Template selbst sowie datumsspezifische Abweichungen (Overrides).
- **FR-027** Wird ein Template geändert, müssen alle zukünftigen, nicht übersteuerten Termine automatisch gemäß neuer Template-Definition wirksam werden.
- **FR-028** Bereits übersteuerte Termine behalten ihre individuellen Anpassungen bei Template-Änderungen.
- **FR-029** Admin kann zusätzliche individuelle Einheiten planen, die keinem Template entsprechen (ad-hoc Einzeltermine).

### 6.4 Aktivitäten

- **FR-030** Admin kann Aktivitäten innerhalb einer Einheit verwalten.
- **FR-031** Aktivitäten enthalten mindestens Typ, Startzeit, Dauer und optionale Themen.
- **FR-032** Das System zeigt Aktivitäten in fachlich korrekter Reihenfolge.
- **FR-033** Das System muss Positionsbezüge für Aktivitäten unterstützen (z. B. `OL`, `DL`, `LB`, `RB`, `DB`, `TE`, `WR`, `QB`) und erweiterbar halten.
- **FR-034** Eine Aktivität kann einer oder mehreren Positionen gleichzeitig zugeordnet werden.
- **FR-035** Das System muss frei definierbare Positionsgruppen unterstützen (z. B. `Line = OL+DL`, `Skill = WR+RB+TE`).
- **FR-036** Eine Aktivität kann einer oder mehreren Positionsgruppen zugeordnet werden; Gruppen dürfen mehrere Positionen enthalten.
- **FR-037** Positions- und Gruppenzuordnungen pro Aktivität müssen analog v1 pro Termin/Template nutzbar und bearbeitbar sein.
- **FR-038** Das System muss die effektive Zielmenge je Aktivität aus den zugeordneten Positionen und Gruppen auflösen können.

### 6.5 Live-Ansicht

- **FR-040** Das System bietet eine Live-Ansicht für den Ablauf einer Einheit.
- **FR-041** Die Live-Ansicht zeigt den aktuellen/kommenden Aktivitätsstatus.
- **FR-042** Die Ansicht muss für den Einsatz während des Trainings bedienbar sein.
- **FR-043** Die aktuell aktive Aktivität muss in der Live-Ansicht deutlich visuell hervorgehoben sein.
- **FR-044** Die Live-Ansicht muss einen Timer mit verbleibender Dauer der aktiven Aktivität anzeigen (Countdown).
- **FR-045** Bei Erreichen eines konfigurierbaren Vorwarnpunkts vor Ablauf muss eine deutliche Warnung ausgelöst werden (optisch und/oder akustisch).
- **FR-046** Beim Ablauf der aktiven Aktivität muss eine Warnung eindeutig erkennbar ausgelöst werden (optisch und/oder akustisch).

### 6.6 Administration

- **FR-050** Admin kann relevante Stammdaten konfigurieren.
- **FR-051** Das System muss Basisfunktionen für Datensicherung und Wiederherstellung unterstützen.

## 7. Nicht-funktionale Anforderungen

### 7.1 Sicherheit

- **NFR-001** Passwörter werden niemals im Klartext persistent gespeichert.
- **NFR-002** Sitzungen müssen gegen offensichtliche Angriffe abgesichert sein.
- **NFR-003** Administrative Aktionen müssen authentifiziert und autorisiert sein.

### 7.2 Qualität und Wartbarkeit

- **NFR-010** Die Architektur folgt den dokumentierten Layern (Domain/Application/Infrastructure/Interface).
- **NFR-011** Kern-Use-Cases müssen automatisiert testbar sein.
- **NFR-012** Anforderungen und APIs müssen versioniert dokumentiert werden.

### 7.3 Betrieb

- **NFR-020** Das System stellt Health-Endpunkte für Live/Ready bereit.
- **NFR-021** Fehler müssen nachvollziehbar protokolliert werden.
- **NFR-022** Konfiguration erfolgt über Umgebungsvariablen.

### 7.4 Performance

- **NFR-030** Standardaktionen im UI antworten im Normalbetrieb typischerweise unter 1 Sekunde.
- **NFR-031** Listenansichten sollen auch bei wachsendem Datenbestand responsiv bleiben.

## 8. Fachliche Datenobjekte (erste Sicht)

- **User**: Benutzername, Rolle, Anmeldedaten
- **Training**: Name, Wochentag, Start/Ende, Startzeit, Sichtbarkeit
- **TrainingTemplate**: Bezug zu Training, Gültigkeit von/bis, Wochentag, Startzeit, Aktivitätsvorgaben
- **TrainingOverride**: Bezug zu Template + Datum, enthält nur abweichende Felder gegenüber Template
- **TrainingInstance**: Konkreter Termin für ein Datum (entweder aus Template abgeleitet, über Override angepasst oder ad-hoc individuell)
- **Position**: Fachliche Positionskennung (z. B. `OL`, `DL`, `LB`)
- **PositionGroup**: Freie Gruppierung aus einer oder mehreren Positionen
- **Activity**: Typ, Startzeit, Dauer, Inhalte/Topics, Reihenfolge, Positionen/Gruppen-Zuordnung

## 9. Akzeptanzkriterien (MVP-Ebene)

- Login mit `admin`/`admin` und `coach`/`coach` ist möglich.
- Admin kann ein Training inkl. mindestens einer Einheit und Aktivität anlegen.
- Coach kann Trainings- und Live-Ansicht ohne Admin-Funktionen nutzen.
- Ein Template mit Zeitraum `01.03.2026` bis `31.03.2026`, Wochentag `Mittwoch`, Startzeit `19:30` erzeugt für alle Mittwoche im März automatisch Einheiten.
- Bei einer Aktivitätssumme von `120` Minuten ergibt sich für diese Termine eine berechnete Endzeit von `21:30`.
- Eine Aktivität kann gleichzeitig mehreren Positionen (z. B. `OL` und `DL`) zugeordnet werden.
- Eine frei definierte Gruppe (z. B. `Line`) kann mehrere Positionen enthalten und in Aktivitäten ausgewählt werden.
- Die effektive Teilnehmer-Zielmenge einer Aktivität wird aus Positions- und Gruppenzuordnungen korrekt zusammengeführt.
- Wird ein einzelner März-Termin angepasst, bleibt nur dieser Termin abweichend; andere Termine folgen weiter dem Template.
- Wird das Template geändert, übernehmen alle zukünftigen nicht angepassten Termine automatisch die Änderung.
- Zusätzliche ad-hoc Einzeltermine können außerhalb oder innerhalb eines Template-Zeitraums separat geplant werden.
- In der Live-Ansicht ist die aktuell aktive Aktivität klar stärker hervorgehoben als andere Aktivitäten.
- In der Live-Ansicht wird die verbleibende Dauer der aktiven Aktivität als Countdown angezeigt.
- Vor Ablauf und bei Ablauf der aktiven Aktivität wird eine deutliche Warnung ausgelöst (mindestens optisch, optional zusätzlich akustisch).
- Health-Endpunkte liefern erwartete Antworten.
- Für Kernfunktionen existieren automatisierte Tests.

## 10. Risiken und offene Punkte

- Finales Rollenmodell (feingranulare Rechte vs. einfache Rollen)
- Zielbild für Datenmigration aus Legacy
- Detailtiefe der Backup/Restore-Prozesse
- Priorisierung der Live-Funktionalität im MVP

## 11. Rückverfolgbarkeit

Anforderungen werden in Implementierung und Tests über IDs referenziert (z. B. `FR-010`, `NFR-020`).

## 12. Änderungsprotokoll

- **2026-02-27**: Erstfassung REQUIREMENTS für Refactoring v2 erstellt.
- **2026-02-27**: Trainingseinheiten um Template-/Override-Modell, Redundanzregeln und ad-hoc Einzeltermine erweitert.
- **2026-02-27**: Rollenbezeichnung für operative Nutzung von `user` auf `coach` angepasst.
- **2026-02-27**: Template-Endzeit entfernt; Endzeit wird aus Startzeit und Aktivitätssumme berechnet.
- **2026-02-27**: Aktivitätslogik um Positions- und frei definierbare Gruppen-Zuordnungen (analog v1) erweitert.
- **2026-02-27**: Live-Ansicht um klare Aktivitäts-Hervorhebung, Countdown und Ablauf-/Vorablaufwarnung erweitert.
