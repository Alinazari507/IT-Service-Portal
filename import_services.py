import sqlite3
import json
import os

# Pfad zur Datenbank und zur JSON-Datei
DB_PATH = 'data/catalog.db'
JSON_PATH = 'data/services.json'

def import_data():
    if not os.path.exists(JSON_PATH):
        print(f"Fehler: {JSON_PATH} wurde nicht gefunden!")
        return

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        services = json.load(f)

    for s in services:
        try:
            c.execute('''
                INSERT OR REPLACE INTO services 
                (id, name, category, availability, description_business, description_technical, sla, costs)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                s.get('id'), s.get('name'), s.get('category'), 
                s.get('availability'), s.get('description_business'), 
                s.get('description_technical'), s.get('sla'), s.get('costs')
            ))
            print(f"Service {s.get('name')} wurde importiert.")
        except Exception as e:
            print(f"Fehler beim Import von {s.get('name')}: {e}")

    conn.commit()
    conn.close()
    print("--- Import abgeschlossen! ---")

if __name__ == '__main__':
    import_data()