# ADR-0001: Architektur-Stil

## Status

Proposed

## Kontext

Das Projekt startet als v2-Refactoring mit Legacy-Archiv in `archive/v1`.
Es wird eine Struktur benötigt, die Fachlogik, Web-Layer und Infrastruktur sauber trennt.

## Entscheidung

Es wird eine geschichtete Architektur mit den Schichten Domain, Application, Infrastructure und Interface verwendet.

## Konsequenzen

- Bessere Testbarkeit der Kernlogik
- Mehr Initialaufwand bei Struktur und Schnittstellen
- Klarere Verantwortlichkeiten pro Modul

## Alternativen

- Klassischer Flask-Monolith ohne klare Layer
- Vollständiger Wechsel auf ein neues Framework
