# 🌐 IT-Service-Portal & Asset Management (CMDB)

Ein modernes, benutzerfreundliches Portal zur Verwaltung von IT-Dienstleistungen, Hardware-Bestellungen und Inventar-Management (ITSM).

## 🚀 Key Features

### 👤 Für Benutzer (Mitarbeiter)
- **Service-Katalog:** Einfache Bestellung von Hardware (Lenovo, Apple) und Software (Microsoft 365, VPN).
- **TCO-Logik:** Automatische Anzeige der Kosten und Verfügbarkeit.
- **Request-Tracking:** Verfolgung des eigenen Ticket-Status (Wartend, In Bearbeitung, Abgeschlossen).

### 🛠️ Für Administratoren (IT-Management)
- **Live-Dashboard:** Grafische Übersicht über offene Tickets und den Wert des Inventars.
- **Full Ticketing System:** Workflow-Management für IT-Anfragen.
- **CMDB (Asset Management):** Registrierung von Geräten mit Asset-Tags, Seriennummern und Standort.
- **Live-Suche & Filter:** Schnelles Auffinden von Tickets und Hardware-Komponenten.
- **Reporting:** Export aller Daten in **Microsoft Excel (.xlsx)** für Management-Berichte.

## ⚙️ Technologien & Frameworks
- **Backend:** Python 3.11+ mit **Flask**
- **Datenbank:** SQLite3 (leichtgewichtig und portabel)
- **Frontend:** HTML5, CSS3 (Custom UI), JavaScript (Live-Search Logik)
- **Reporting-Engine:** Pandas & OpenPyxl
- **Security:** Flask-Login & Dotenv (Umgebungsvariablen)

---

## 🛠️ Installation & Setup

1. **Repository klonen:**
   ```bash
   git clone [https://github.com/Alinazari507/IT-Service-Portal.git](https://github.com/Alinazari507/IT-Service-Portal.git)
   cd IT-Service-Portal