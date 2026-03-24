# database.py
import sqlite3
import json

DB_PATH = 'data/catalog.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # جدول سرویس‌ها
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
    # جدول درخواست‌ها
    c.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_id TEXT,
            user_name TEXT,
            user_dept TEXT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (service_id) REFERENCES services(id)
        )
    ''')
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
    # تبدیل به لیست دیکشنری
    services = []
    for row in rows:
        services.append({
            'id': row[0],
            'name': row[1],
            'category': row[2],
            'availability': row[3],
            'description_business': row[4],
            'description_technical': row[5],
            'sla': row[6],
            'costs': row[7],
            'active': row[8]
        })
    return services

def get_service(service_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM services WHERE id=?", (service_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            'id': row[0],
            'name': row[1],
            'category': row[2],
            'availability': row[3],
            'description_business': row[4],
            'description_technical': row[5],
            'sla': row[6],
            'costs': row[7],
            'active': row[8]
        }
    return None

def add_service(service):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO services (id, name, category, availability, description_business, description_technical, sla, costs)
        VALUES (?,?,?,?,?,?,?,?)
    ''', (service['id'], service['name'], service['category'], service['availability'],
          service['description_business'], service['description_technical'], service['sla'], service['costs']))
    conn.commit()
    conn.close()

def add_request(service_id, user_name, user_dept):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO requests (service_id, user_name, user_dept, status)
        VALUES (?,?,?,?)
    ''', (service_id, user_name, user_dept, 'Pending'))
    conn.commit()
    conn.close()
    return c.lastrowid

def get_requests(user_name=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if user_name:
        c.execute("SELECT * FROM requests WHERE user_name=? ORDER BY created_at DESC", (user_name,))
    else:
        c.execute("SELECT * FROM requests ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    requests = []
    for row in rows:
        requests.append({
            'id': row[0],
            'service_id': row[1],
            'user_name': row[2],
            'user_dept': row[3],
            'status': row[4],
            'created_at': row[5]
        })
    return requests