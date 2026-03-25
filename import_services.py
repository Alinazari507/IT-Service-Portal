import sqlite3
import os
import json

# Pfad zur Datenbank und zur JSON-Datei
DB_PATH = 'data/v4_final.db'
JSON_PATH = 'data/services.json'

if not os.path.exists('data'):
    os.makedirs('data')

def init_db():
    """Initialisiert die Datenbank mit den neuen CMDB-Strukturen."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Tabelle für IT-Services
    c.execute('''CREATE TABLE IF NOT EXISTS services (
        id TEXT PRIMARY KEY, name TEXT NOT NULL, category TEXT, availability TEXT, 
        description_business TEXT, description_technical TEXT, sla TEXT, costs TEXT, active INTEGER DEFAULT 1)''')

    # Tabelle für Service-Anfragen (Tickets)
    c.execute('''CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT, service_id TEXT, user_name TEXT, 
        user_dept TEXT, status TEXT, reason TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    # Tabelle für Benutzer
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, 
        password TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'user', fullname TEXT, department TEXT)''')

    # Erweiterte CMDB Tabelle nach Ihren Wünschen
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        asset_tag TEXT UNIQUE,          -- ID (Asset-Tag)
        geraetetyp TEXT,                -- Gerätetyp
        hersteller_modell TEXT,         -- Hersteller/Modell
        seriennummer TEXT,              -- Seriennummer
        kaufdatum TEXT,                 -- Kaufdatum
        status TEXT,                    -- Status (z.B. Im Lager, Zugewiesen, Bestellt)
        nutzer_standort TEXT,           -- Nutzer/Standort
        garantie_bis TEXT,              -- Garantie bis
        lizenz_bis TEXT,                 -- Lizenz bis
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Standard-Admin erstellen
    c.execute("SELECT * FROM users WHERE username = 'admin'")
    if not c.fetchone():
        c.execute("INSERT INTO users (username, password, role, fullname, department) VALUES (?, ?, ?, ?, ?)",
                  ('admin', 'Kein-Zugriff-fur-User-2026!', 'admin', 'System Administrator', 'IT Management'))

    conn.commit()
    conn.close()
    import_data() # Importiert Services aus JSON falls vorhanden

def import_data():
    """Importiert Services aus einer JSON-Datei in die Datenbank."""
    if not os.path.exists(JSON_PATH):
        return

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            services = json.load(f)
        for s in services:
            c.execute('''INSERT OR REPLACE INTO services 
                (id, name, category, availability, description_business, description_technical, sla, costs)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                (s.get('id'), s.get('name'), s.get('category'), s.get('availability'), 
                 s.get('description_business'), s.get('description_technical'), s.get('sla'), s.get('costs')))
        conn.commit()
    except Exception as e:
        print(f"Fehler beim Import: {e}")
    finally:
        conn.close()

def get_inventory():
    """Gibt alle Inventar-Einträge als Liste von Dictionaries zurück."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("SELECT id, asset_tag, geraetetyp, hersteller_modell, seriennummer, kaufdatum, status, nutzer_standort, garantie_bis, lizenz_bis FROM inventory")
        rows = c.fetchall()
        return [{'id': r[0], 'asset_tag': r[1], 'geraetetyp': r[2], 'hersteller_modell': r[3], 
                 'seriennummer': r[4], 'kaufdatum': r[5], 'status': r[6], 'nutzer_standort': r[7], 
                 'garantie_bis': r[8], 'lizenz_bis': r[9]} for r in rows]
    except:
        return []
    finally:
        conn.close()

def add_inventory_item(data):
    """Fügt ein neues Asset zur CMDB hinzu."""
    conn = sqlite3.connect(DB_PATH)
    try:
        c = conn.cursor()
        c.execute('''INSERT INTO inventory 
            (asset_tag, geraetetyp, hersteller_modell, seriennummer, kaufdatum, status, nutzer_standort, garantie_bis, lizenz_bis) 
            VALUES (?,?,?,?,?,?,?,?,?)''', 
            (data['asset_tag'], data['geraetetyp'], data['hersteller_modell'], 
             data['seriennummer'], data['kaufdatum'], data['status'], 
             data['nutzer_standort'], data['garantie_bis'], data['lizenz_bis']))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

# --- Funktionen für Services & Requests ---

def get_services(category=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if category:
        c.execute("SELECT * FROM services WHERE category=? AND active=1", (category,))
    else:
        c.execute("SELECT * FROM services WHERE active=1")
    rows = c.fetchall()
    conn.close()
    return [{'id': r[0], 'name': r[1], 'category': r[2], 'availability': r[3], 'description_business': r[4], 'description_technical': r[5], 'sla': r[6], 'costs': r[7]} for r in rows]

def get_service(service_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM services WHERE id=?", (service_id,))
    row = c.fetchone()
    conn.close()
    return {'id': row[0], 'name': row[1], 'category': row[2], 'availability': row[3], 'description_business': row[4], 'description_technical': row[5], 'sla': row[6], 'costs': row[7]} if row else None

def add_request(service_id, user_name, user_dept, reason=""):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO requests (service_id, user_name, user_dept, status, reason) VALUES (?,?,?,?,?)", (service_id, user_name, user_dept, 'Pending', reason))
    conn.commit()
    conn.close()

def get_requests(user_name=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if user_name:
        c.execute("SELECT id, service_id, user_name, user_dept, status, reason, created_at FROM requests WHERE user_name=? ORDER BY created_at DESC", (user_name,))
    else:
        c.execute("SELECT id, service_id, user_name, user_dept, status, reason, created_at FROM requests ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    return [{'id': r[0], 'service_id': r[1], 'user_name': r[2], 'user_dept': r[3], 'status': r[4], 'reason': r[5], 'date': r[6]} for r in rows]

def update_request_status(request_id, new_status, admin_note=""):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if admin_note:
        c.execute("UPDATE requests SET status = ?, reason = ? WHERE id = ?", (new_status, admin_note, request_id))
    else:
        c.execute("UPDATE requests SET status = ? WHERE id = ?", (new_status, request_id))
    conn.commit()
    conn.close()

def get_user(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    return {'id': row[0], 'username': row[1], 'password': row[2], 'role': row[3], 'fullname': row[4], 'department': row[5]} if row else None

def add_user(username, password, role='user', fullname='', department=''):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password, role, fullname, department) VALUES (?, ?, ?, ?, ?)", (username, password, role, fullname, department))
    conn.commit()
    conn.close()

def get_ticket_stats():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT status, COUNT(*) FROM requests GROUP BY status")
    stats = dict(c.fetchall())
    conn.close()
    return {'Pending': stats.get('Pending', 0), 'In Progress': stats.get('In Progress', 0), 'Completed': stats.get('Completed', 0), 'Approved': stats.get('Approved', 0), 'Rejected': stats.get('Rejected', 0)}

def get_inventory_count():
    conn = sqlite3.connect(DB_PATH)
    count = conn.execute("SELECT COUNT(*) FROM inventory").fetchone()[0]
    conn.close()
    return count