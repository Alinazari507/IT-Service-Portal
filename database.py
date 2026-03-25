import sqlite3
import os

# Erstellt den Ordner 'data', falls er nicht existiert
if not os.path.exists('data'):
    os.makedirs('data')

DB_PATH = 'data/catalog.db'

def init_db():
    """Initialisiert die Datenbanktabellen und Startdaten."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Tabelle für IT-Services
    c.execute('''
        CREATE TABLE IF NOT EXISTS services (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            availability TEXT,
            description_business TEXT,
            description_technical TEXT,
            sla TEXT,
            costs TEXT,
            active INTEGER DEFAULT 1
        )
    ''')

    # Tabelle für Service-Anfragen (Tickets)
    c.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_id TEXT,
            user_name TEXT,
            user_dept TEXT,
            status TEXT,
            reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (service_id) REFERENCES services(id)
        )
    ''')

    # Tabelle für Benutzer
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            fullname TEXT,
            department TEXT
        )
    ''')

    # Tabelle für IT-Inventory (CMDB)
    c.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_tag TEXT UNIQUE,
            item_name TEXT,
            serial_number TEXT,
            assigned_to TEXT,
            status TEXT,
            location TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Standard-Admin erstellen, falls nicht vorhanden
    c.execute("SELECT * FROM users WHERE username = 'admin'")
    if not c.fetchone():
        secure_password = "Kein-Zugriff-fur-User-2026!"
        c.execute('''
            INSERT INTO users (username, password, role, fullname, department)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', secure_password, 'admin', 'System Administrator', 'IT Management'))

    conn.commit()
    conn.close()
    
    # Standard-Services hinzufügen
    seed_data()

def seed_data():
    """Füllt die Datenbank mit Standard-Services, falls keine vorhanden sind."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM services")
    if c.fetchone()[0] == 0:
        services = [
            ('HW-001', 'Lenovo ThinkPad X1', 'Hardware', 'Sofort verfügbar', 
             'Premium Business Notebook für mobiles Arbeiten.', 
             'Intel i7, 16GB RAM, 512GB SSD, Windows 11 Pro.', '3 Werktage', '0€ (Standard)'),
            
            ('SW-002', 'Microsoft 365 Business', 'Software', '24h Aktivierung', 
             'Vollständiges Office-Paket für produktives Arbeiten.', 
             'Enthält Word, Excel, Teams und Outlook.', '1 Werktag', '12,50€ / Monat'),
            
            ('ACC-003', 'VPN-Fernzugriff', 'Zugang', 'Sofort', 
             'Sicherer Zugriff auf das Firmennetzwerk von Zuhause.', 
             'Cisco AnyConnect mit Multi-Faktor-Authentifizierung.', '1 Stunde', '0€'),
            
            ('SUP-004', 'IT-Support Ticket', 'Support', 'Mo-Fr 08:00-17:00', 
             'Unterstützung bei technischen Problemen aller Art.', 
             'Support über Jira Service Management System.', '4 Stunden', '0€')
        ]
        c.executemany('''
            INSERT INTO services (id, name, category, availability, description_business, description_technical, sla, costs) 
            VALUES (?,?,?,?,?,?,?,?)
        ''', services)
        conn.commit()
    conn.close()

def get_services(category=None):
    """Gibt alle aktiven Services zurück."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if category:
        c.execute("SELECT * FROM services WHERE category=? AND active=1", (category,))
    else:
        c.execute("SELECT * FROM services WHERE active=1")
    rows = c.fetchall()
    conn.close()
    
    services = []
    for r in rows:
        services.append({
            'id': r[0], 'name': r[1], 'category': r[2], 'availability': r[3],
            'description_business': r[4], 'description_technical': r[5],
            'sla': r[6], 'costs': r[7]
        })
    return services

def get_service(service_id):
    """Sucht einen einzelnen Service nach ID."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM services WHERE id=?", (service_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            'id': row[0], 'name': row[1], 'category': row[2], 'availability': row[3],
            'description_business': row[4], 'description_technical': row[5],
            'sla': row[6], 'costs': row[7]
        }
    return None

def add_request(service_id, user_name, user_dept, reason=""):
    """Speichert eine neue Service-Anfrage."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO requests (service_id, user_name, user_dept, status, reason)
        VALUES (?,?,?,?,?)
    ''', (service_id, user_name, user_dept, 'Pending', reason))
    conn.commit()
    conn.close()

def get_requests(user_name=None):
    """Ruft Anfragen für einen bestimmten Benutzer oder alle ab."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if user_name:
        c.execute("SELECT * FROM requests WHERE user_name=? ORDER BY created_at DESC", (user_name,))
    else:
        c.execute("SELECT * FROM requests ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    
    requests_list = []
    for r in rows:
        requests_list.append({
            'id': r[0], 'service_id': r[1], 'user_name': r[2],
            'user_dept': r[3], 'status': r[4], 'reason': r[5], 'created_at': r[6]
        })
    return requests_list

def add_service(service):
    """Fügt einen neuen Service hinzu (Admin-Funktion)."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO services (id, name, category, availability, description_business, description_technical, sla, costs)
        VALUES (?,?,?,?,?,?,?,?)
    ''', (service['id'], service['name'], service['category'], service['availability'],
          service['description_business'], service['description_technical'], service['sla'], service['costs']))
    conn.commit()
    conn.close()

def get_user(username):
    """Sucht einen Benutzer anhand des Benutzernamens."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    if row:
        return {'id': row[0], 'username': row[1], 'password': row[2], 'role': row[3], 'fullname': row[4], 'department': row[5]}
    return None

def add_user(username, password, role='user', fullname='', department=''):
    """Registriert einen neuen Benutzer in der Datenbank."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password, role, fullname, department) VALUES (?, ?, ?, ?, ?)", 
              (username, password, role, fullname, department))
    conn.commit()
    conn.close()

def get_all_requests():
    """Hilfsfunktion: Gibt alle Anfragen für das Admin-Panel zurück."""
    return get_requests(user_name=None)

def update_request_status(request_id, new_status):
    """Aktualisiert den Status einer bestehenden Anfrage."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE requests SET status = ? WHERE id = ?", (new_status, request_id))
    conn.commit()
    conn.close()

# --- Funktionen für CMDB (Inventory) ---

def get_inventory():
    """Ruft die gesamte Inventarliste ab."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM inventory ORDER BY asset_tag ASC")
    rows = c.fetchall()
    conn.close()
    return rows

def add_inventory_item(tag, name, sn, user, status, loc):
    """Fügt ein neues Gerät zum IT-Inventar hinzu."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO inventory (asset_tag, item_name, serial_number, assigned_to, status, location)
            VALUES (?,?,?,?,?,?)
        ''', (tag, name, sn, user, status, loc))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False # Falls Asset Tag doppelt vergeben wird
    conn.close()
    return success

# --- Funktionen für Dashboard-Statistiken ---

def get_ticket_stats():
    """Berechnet die Anzahl der Tickets pro Status für das Dashboard."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("SELECT status, COUNT(*) FROM requests GROUP BY status")
    stats = dict(c.fetchall())
    
    # Sicherstellen, dass alle Status-Keys vorhanden sind
    result = {
        'Pending': stats.get('Pending', 0),
        'In Progress': stats.get('In Progress', 0),
        'Completed': stats.get('Completed', 0)
    }
    conn.close()
    return result

def get_inventory_count():
    """Gibt die Gesamtanzahl der registrierten Geräte zurück."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM inventory")
    count = c.fetchone()[0]
    conn.close()
    return count
