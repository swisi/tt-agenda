def test_admin_backup_page_shows_sqlite_actions_for_sqlite(client, login_as):
    login_as(username='admin', password='secret', role='admin')

    response = client.get('/admin/backup')

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'SQLite' in html
    assert 'Backup herunterladen' in html
    assert 'Backup hochladen &amp; wiederherstellen' in html


def test_admin_backup_page_shows_postgres_guidance_for_non_sqlite(client, login_as, monkeypatch):
    from app.routes import admin as admin_routes

    login_as(username='admin', password='secret', role='admin')
    monkeypatch.setattr(admin_routes, 'get_database_backend', lambda: 'postgresql')
    monkeypatch.setattr(admin_routes, 'resolve_sqlite_db_path', lambda: None)

    response = client.get('/admin/backup')

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert 'PostgreSQL' in html
    assert 'pg_dump' in html


def test_admin_backup_download_redirects_for_non_sqlite(client, login_as, monkeypatch):
    from app.routes import admin as admin_routes

    login_as(username='admin', password='secret', role='admin')
    monkeypatch.setattr(admin_routes, 'get_database_backend', lambda: 'postgresql')

    response = client.get('/admin/backup/download', follow_redirects=False)

    assert response.status_code == 302
    assert response.headers['Location'].endswith('/admin/backup')
