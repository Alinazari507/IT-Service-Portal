import sqlite3
import os

if not os.path.exists('data'):
    os.makedirs('data')

DB_PATH = 'data/catalog.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

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
    
    c.execute("SELECT * FROM users WHERE username = 'admin'")
    if not c.fetchone():
        secure_password = "Kein-Zugriff-fur-User-2026!"
        c.execute('''
            INSERT INTO users (username, password, role, fullname, department)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', secure_password, 'admin', 'System Administrator', 'IT Management'))

    conn.commit()
    conn.close()
    seed_data()

def seed_data():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM services")
    if c.fetchone()[0] == 0:
        services = [
            ('HW-001', 'Lenovo ThinkPad X1', 'Hardware', 'Sofort verfügbar', 
             'Premium Business Notebook.', 'i7, 16GB RAM, 512GB SSD.', '3 Werktage', '0€'),
            ('SW-002', 'Microsoft 365 Business', 'Software', '24h Aktivierung', 
             'Office-Paket (Word, Excel, Teams).', 'Cloud-Lizenz.', '1 Werktag', '12,50€'),
            ('ACC-003', 'VPN-Fernzugriff', 'Zugang', 'Sofort', 
             'Sicherer Zugriff auf das Firmennetzwerk.', 'Cisco MFA.', '1 Stunde', '0€')
        ]
        c.executemany("INSERT INTO services VALUES (?,?,?,?,?,?,?,?,1)", services)
        conn.commit()
    conn.close()

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

def get_all_requests():
    return get_requests()

def update_request_status(request_id, new_status):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
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

def add_service(service):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO services (id, name, category, availability, description_business, description_technical, sla, costs) VALUES (?,?,?,?,?,?,?,?)", (service['id'], service['name'], service['category'], service['availability'], service['description_business'], service['description_technical'], service['sla'], service['costs']))
    conn.commit()
    conn.close()

def get_inventory():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, asset_tag, item_name, serial_number, assigned_to, status, location FROM inventory ORDER BY asset_tag ASC")
    rows = c.fetchall()
    conn.close()
    return rows

def add_inventory_item(tag, name, sn, user, status, loc):
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("INSERT INTO inventory (asset_tag, item_name, serial_number, assigned_to, status, location) VALUES (?,?,?,?,?,?)", (tag, name, sn, user, status, loc))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def get_ticket_stats():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT status, COUNT(*) FROM requests GROUP BY status")
    stats = dict(c.fetchall())
    conn.close()
    return {'Pending': stats.get('Pending', 0), 'In Progress': stats.get('In Progress', 0), 'Completed': stats.get('Completed', 0), 'Approved': stats.get('Approved', 0)}

def get_inventory_count():
    conn = sqlite3.connect(DB_PATH)
    count = conn.execute("SELECT COUNT(*) FROM inventory").fetchone()[0]
    conn.close()
    return count