# Architektur (v2)

## Ziele

- Entkopplung von Web-UI, Geschäftslogik und Persistenz
- Hohe Testbarkeit im Domain/Application-Layer
- Erweiterbarkeit ohne Seiteneffekte

## Geplante Schichten

1. **Domain**
   - Entitäten, Value Objects, Domain Services
   - Keine Framework-Abhängigkeiten

2. **Application**
   - Use Cases (z. B. Login, Trainingsplanung, Live-Status)
   - Orchestrierung der Domain

3. **Infrastructure**
   - Datenbankzugriff, externe Integrationen, Migrations
   - Implementiert Interfaces aus Application/Domain

4. **Interface/Presentation**
   - Flask Blueprints/HTTP-Controller
   - Templates/Frontend-spezifische Darstellung

## Architekturentscheidungen (ADR)

Wichtige Entscheidungen werden in `docs/adr/` dokumentiert.

- ADR-0001: Architektur-Stil
- ADR-0002: Persistenzstrategie
- ADR-0003: Authentifizierungskonzept

## Offene Punkte

- Auth-Strategie (lokal vs. IdP)
- Multi-Umgebungs-Konfiguration
- Deployment-Topologie
