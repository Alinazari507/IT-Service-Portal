import sqlite3
import database

def populate_services():
    # Verbindung zur Datenbank herstellen
    conn = sqlite3.connect(database.DB_PATH)
    c = conn.cursor()

    # Beispieldaten für den Service-Katalog (Basierend auf deinen Bildern)
    services = [
        ('HW-001', 'Lenovo ThinkPad X1', 'Hardware', 'Sofort', 
         'Hochwertiges Notebook für mobiles Arbeiten mit langer Akkulaufzeit.', 
         'Intel i7, 16GB RAM, 512GB SSD, Windows 11 Pro.', '3 Werktage', 'kostenfrei'),
        
        ('SW-002', 'Microsoft 365 E3', 'Software', '24h', 
         'Vollständiges Office-Paket inkl. OneDrive und Teams.', 
         'Lizenzzuweisung über Azure AD / Entra ID.', '1 Werktag', '12€ / Monat'),
        
        ('ACC-003', 'VPN-Zugang', 'Zugang', 'sofort', 
         'Sicherer Fernzugriff auf das Firmennetzwerk von überall.', 
         'Cisco AnyConnect Client, MFA erforderlich.', '1 Stunde', 'kostenfrei'),
        
        ('SUP-004', 'IT-Support Vor-Ort', 'Support', 'nach Vereinbarung', 
         'Persönliche Unterstützung bei Hardware-Problemen am Arbeitsplatz.', 
         'Ticket-Erstellung über Jira Service Management.', '4 Stunden', 'kostenfrei')
    ]

    # Daten in die Tabelle 'services' einfügen
    c.executemany('''
        INSERT OR REPLACE INTO services 
        (id, name, category, availability, description_business, description_technical, sla, costs) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', services)

    conn.commit()
    conn.close()
    print("✅ Der Service-Katalog wurde erfolgreich mit Beispieldaten gefüllt!")

if __name__ == '__main__':
    # Sicherstellen, dass die Tabellen existieren
    database.init_db()
    # Daten einfügen
    populate_services()