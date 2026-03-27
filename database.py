import sqlite3
import os

if not os.path.exists('data'):
    os.makedirs('data')

DB_PATH = 'data/v10_full_fixed.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS services (
        id TEXT PRIMARY KEY, name TEXT NOT NULL, category TEXT, availability TEXT, 
        description_business TEXT, description_technical TEXT, sla TEXT, costs TEXT, active INTEGER DEFAULT 1)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT, service_id TEXT, user_name TEXT, 
        user_dept TEXT, status TEXT, reason TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, 
        password TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'user', fullname TEXT, department TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT, asset_tag TEXT UNIQUE, geraetetyp TEXT, 
        hersteller_modell TEXT, seriennummer TEXT, kaufdatum TEXT, status TEXT, 
        nutzer_standort TEXT, garantie_bis TEXT, lizenz_bis TEXT, last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    c.execute("SELECT * FROM users WHERE username = 'admin'")
    if not c.fetchone():
        c.execute("INSERT INTO users (username, password, role, fullname, department) VALUES (?, ?, ?, ?, ?)",
                  ('admin', 'Kein-Zugriff-fur-User-2026!', 'admin', 'System Administrator', 'IT Management'))
    
    conn.commit()
    conn.close()
    seed_data()

def seed_data():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM services")
    if c.fetchone()[0] == 0:
        services = [
            ('HW-001', 'Lenovo ThinkPad X1', 'Hardware', 'Sofort verfügbar', 'Premium Business Notebook für mobiles Arbeiten.', 'Intel i7, 16GB RAM, 512GB SSD', '3 Werktage', '0€ (Standard)'),
            ('SW-001', 'Adobe Acrobat Pro', 'Software', '24h Aktivierung', 'Vollständiges PDF-Management-Tool.', 'Acrobat DC Enterprise', '1 Werktag', '15,00€ / Monat'),
            ('ACC-001', 'VPN-Fernzugriff', 'Zugang & Berechtigungen', 'Sofort', 'Sicherer Zugriff auf das Firmennetzwerk von Zuhause.', 'GlobalProtect Client Connection', '1 Stunde', '0€'),
            ('SUP-001', 'IT-Support Ticket', 'Support', 'Mo-Fr 08:00-17:00', 'Unterstützung bei technischen Problemen aller Art.', 'First Level & Technical Support', '4 Stunden', '0€')
        ]
        c.executemany("INSERT INTO services (id, name, category, availability, description_business, description_technical, sla, costs, active) VALUES (?,?,?,?,?,?,?,?,1)", services)
        conn.commit()
    conn.close()

def get_services(category=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if category and category != 'Alle':
        c.execute("SELECT id, name, category, availability, description_business, description_technical, sla, costs FROM services WHERE category=? AND active=1", (category,))
    else:
        c.execute("SELECT id, name, category, availability, description_business, description_technical, sla, costs FROM services WHERE active=1")
    rows = c.fetchall()
    conn.close()
    return [{'id': r[0], 'name': r[1], 'category': r[2], 'availability': r[3], 'description_business': r[4], 'description_technical': r[5], 'sla': r[6], 'costs': r[7]} for r in rows]

def get_service(service_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, name, category, availability, description_business, description_technical, sla, costs FROM services WHERE id=?", (service_id,))
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

def get_all_requests():
    return get_requests()

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
    c.execute("SELECT id, username, password, role, fullname, department FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    return {'id': row[0], 'username': row[1], 'password': row[2], 'role': row[3], 'fullname': row[4], 'department': row[5]} if row else None

def add_user(username, password, role='user', fullname='', department=''):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password, role, fullname, department) VALUES (?, ?, ?, ?, ?)", (username, password, role, fullname, department))
    conn.commit()
    conn.close()

def add_service(s):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO services (id, name, category, availability, description_business, description_technical, sla, costs) VALUES (?,?,?,?,?,?,?,?)", 
              (s['id'], s['name'], s['category'], s['availability'], s['description_business'], s['description_technical'], s['sla'], s['costs']))
    conn.commit()
    conn.close()

def get_ticket_stats():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT status, COUNT(*) FROM requests GROUP BY status")
    stats = dict(c.fetchall())
    conn.close()
    return {
        'Pending': stats.get('Pending', 0), 
        'In Progress': stats.get('In Progress', 0), 
        'Completed': stats.get('Completed', 0), 
        'Approved': stats.get('Approved', 0), 
        'Rejected': stats.get('Rejected', 0)
    }

def get_inventory_count():
    conn = sqlite3.connect(DB_PATH)
    count = conn.execute("SELECT COUNT(*) FROM inventory").fetchone()[0]
    conn.close()
    return count

def get_inventory():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, asset_tag, geraetetyp, hersteller_modell, seriennummer, kaufdatum, status, nutzer_standort, garantie_bis, lizenz_bis FROM inventory")
    rows = c.fetchall()
    conn.close()
    return [{'id': r[0], 'asset_tag': r[1], 'geraetetyp': r[2], 'hersteller_modell': r[3], 
             'seriennummer': r[4], 'kaufdatum': r[5], 'status': r[6], 
             'nutzer_standort': r[7], 'garantie_bis': r[8], 'lizenz_bis': r[9]} for r in rows]

def add_inventory_item(data):
    conn = sqlite3.connect(DB_PATH)
    try:
        c = conn.cursor()
        c.execute('''INSERT INTO inventory 
            (asset_tag, geraetetyp, hersteller_modell, seriennummer, kaufdatum, status, nutzer_standort, garantie_bis, lizenz_bis) 
            VALUES (?,?,?,?,?,?,?,?,?)''', 
            (data.get('asset_tag'), data.get('geraetetyp'), data.get('hersteller_modell'), 
             data.get('seriennummer'), data.get('kaufdatum', ''), data.get('status', 'Im Lager'), 
             data.get('nutzer_standort', ''), data.get('garantie_bis', ''), data.get('lizenz_bis', '')))
        conn.commit()
        return True
    except Exception as e:
        print(f"Database Error: {e}")
        return False
    finally:
        conn.close()