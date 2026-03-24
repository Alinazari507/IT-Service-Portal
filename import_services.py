import json
import sqlite3
import os

DB_PATH = 'data/catalog.db'

def import_services(json_file):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    with open(json_file, 'r', encoding='utf-8') as f:
        services = json.load(f)
    for s in services:
        c.execute('''
            INSERT OR REPLACE INTO services 
            (id, name, category, availability, description_business, description_technical, sla, costs, active)
            VALUES (?,?,?,?,?,?,?,?,1)
        ''', (s['id'], s['name'], s['category'], s['availability'],
              s['description_business'], s['description_technical'], s['sla'], s['costs']))
    conn.commit()
    conn.close()
    print(f"{len(services)} Services importiert.")

if __name__ == '__main__':
    import_services('data/services.json')