import sqlite3
import os

# Erstellt den Ordner 'data', falls er nicht existiert
if not os.path.exists('data'):
    os.makedirs('data')

DB_PATH = 'data/catalog.db'

def init_db():
    """Initialisiert die Datenbanktabellen."""
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

    # Tabelle für Service-Anfragen inkl. Spalte 'reason'
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
    
    # --- بخش اضافه شده برای ادمین همیشگی ---
    # این کد چک می‌کند اگر یوزر ادمین وجود ندارد، آن را بسازد
    c.execute("SELECT * FROM users WHERE username = 'admin'")
    if not c.fetchone():
        # پسورد مورد نظر شما به سبک امن
        secure_password = "Kein-Zugriff-fur-User-2026!"
        c.execute('''
            INSERT INTO users (username, password, role, fullname, department)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', secure_password, 'admin', 'System Administrator', 'IT Management'))
    # ---------------------------------------

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
    """Sucht einen einzelnen Service."""
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
    """Speichert eine neue Anfrage."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO requests (service_id, user_name, user_dept, status, reason)
        VALUES (?,?,?,?,?)
    ''', (service_id, user_name, user_dept, 'Pending', reason))
    conn.commit()
    conn.close()

def get_requests(user_name=None):
    """Ruft Anfragen für einen Benutzer ab."""
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
    """Fügt einen neuen Service hinzu (Admin)."""
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
    """Sucht einen Benutzer."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    if row:
        return {'id': row[0], 'username': row[1], 'password': row[2], 'role': row[3], 'fullname': row[4], 'department': row[5]}
    return None

def add_user(username, password, role='user', fullname='', department=''):
    """Registriert einen neuen Benutzer."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password, role, fullname, department) VALUES (?, ?, ?, ?, ?)", 
              (username, password, role, fullname, department))
    conn.commit()
    conn.close()

def get_all_requests():
    """Gibt alle Anfragen für Admin-Panel zurück."""
    return get_requests(user_name=None)

def update_request_status(request_id, new_status):
    """Aktualisiert Status einer Anfrage."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE requests SET status = ? WHERE id = ?", (new_status, request_id))
    conn.commit()
    conn.close()