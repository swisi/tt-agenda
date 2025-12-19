"""
Migration: Fügt color-Feld zu Activity-Tabelle hinzu
"""
from app import app, db
from sqlalchemy import text

def migrate_add_color():
    """Fügt color-Spalte zur activity Tabelle hinzu."""
    with app.app_context():
        try:
            # Prüfe ob color Spalte existiert
            result = db.session.execute(text("PRAGMA table_info(activity)"))
            columns = [row[1] for row in result]
            
            if 'color' not in columns:
                print("Füge color-Spalte zu activity Tabelle hinzu...")
                db.session.execute(text("""
                    ALTER TABLE activity 
                    ADD COLUMN color VARCHAR(7) DEFAULT '#10b981'
                """))
                # Setze Standard-Farbe für bestehende Einträge
                db.session.execute(text("""
                    UPDATE activity 
                    SET color = '#10b981'
                    WHERE color IS NULL
                """))
                print("✓ activity Tabelle aktualisiert")
            else:
                print("✓ color-Spalte existiert bereits")
            
            db.session.commit()
            print("\n✓ Migration erfolgreich abgeschlossen!")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ Fehler bei der Migration: {str(e)}")
            raise

if __name__ == '__main__':
    print("Starte Migration: color-Feld hinzufügen...")
    migrate_add_color()

