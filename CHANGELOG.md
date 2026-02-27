# Changelog

All notable changes to this project will be documented in this file.

## [v0.2.0] - 2026-02-27

### Added
- Migrated backend to FastAPI with plain SQLAlchemy.
- Server-rendered Jinja2 frontend and Live view (`/`).
- WebSocket live updates at `/ws/live` with optional token auth (`WS_AUTH_TOKEN`).
- Diff-only broadcast mode: server sends `diff` messages when today's schedule changes.
- Client JS updated to consume snapshot + diff messages.
- Tests: WebSocket auth and diff behavior covered by automated tests.

### Changed
- Reorganized project structure under `src/tt_agenda_v2`.

### Fixed
- Various test and startup issues during migration.
