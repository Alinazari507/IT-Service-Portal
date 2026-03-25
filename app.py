import os
import sqlite3
import io
import pandas as pd
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import database
from models import User

# Lade Umgebungsvariablen
load_dotenv()

app = Flask(__name__)
# Sicherheitsschlüssel für Sessions
app.secret_key = os.getenv('SECRET_KEY', 'mein-it-portal-geheimnis-2026')

# Flask-Login Initialisierung
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    """Lädt den Benutzer für die aktuelle Sitzung aus der Datenbank."""
    conn = sqlite3.connect(database.DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, username, role, fullname, department FROM users WHERE id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return User(row[0], row[1], row[2], row[3], row[4])
    return None

# Initialisiere Datenbankstruktur beim Start
database.init_db()

# --- Authentifizierung ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Benutzeranmeldung."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_data = database.get_user(username)
        
        if user_data and user_data['password'] == password:
            user = User(user_data['id'], user_data['username'], user_data['role'],
                        user_data['fullname'], user_data['department'])
            login_user(user)
            session['user'] = user_data['username']
            session['role'] = user_data['role']
            return redirect(url_for('index'))
        else:
            flash('Ungültiger Benutzername oder Passwort')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Benutzerregistrierung."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        fullname = request.form['fullname']
        department = request.form['department']
        
        if database.get_user(username):
            flash('Benutzername existiert bereits.')
            return redirect(url_for('register'))
        
        role = 'admin' if username.lower() == 'admin' else 'user'
        database.add_user(username, password, role, fullname, department)
        flash('Registrierung erfolgreich. Bitte loggen Sie sich ein.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    """Beendet die aktuelle Sitzung."""
    session.clear()
    logout_user()
    return redirect(url_for('login'))

# --- Service Katalog (User) ---

@app.route('/')
@login_required
def index():
    """Startseite mit Service-Übersicht."""
    category = request.args.get('category')
    services = database.get_services(category)
    return render_template('index.html', user=current_user, services=services)

@app.route('/request/<service_id>')
@login_required
def show_request_form(service_id):
    """Zeigt das Anfrageformular برای یک سرویس خاص."""
    service = database.get_service(service_id)
    return render_template('service_request.html', service=service, user=current_user)

@app.route('/request', methods=['POST'])
@login_required
def request_service():
    """Speichert eine neue Service-Anfrage."""
    service_id = request.form['service_id']
    reason = request.form.get('reason', '')
    database.add_request(service_id, current_user.fullname, current_user.department, reason)
    flash('Ihre Anfrage wurde erfolgreich gesendet.')
    return redirect(url_for('requests_list'))

@app.route('/requests')
@login_required
def requests_list():
    """Anzeige der eigenen Anfragen."""
    reqs = database.get_requests(user_name=current_user.fullname)
    return render_template('requests.html', requests=reqs)

# --- Administration & Ticketing (Admin) ---

@app.route('/admin')
@login_required
def admin_panel():
    """Admin Dashboard mit Statistiken."""
    if current_user.role != 'admin':
        flash('Zugriff verweigert.')
        return redirect(url_for('index'))
    
    stats = database.get_ticket_stats()
    inv_count = database.get_inventory_count()
    requests_all = database.get_all_requests()
    
    return render_template('admin.html', requests=requests_all, stats=stats, inv_count=inv_count)

# WICHTIG: Name angepasst an die Formulare in admin.html
@app.route('/admin/update/<int:request_id>', methods=['POST'])
@login_required
def admin_update_request(request_id):
    """Status-Update einer Anfrage über das Admin-Panel."""
    if current_user.role != 'admin':
        return "Zugriff verweigert", 403
    
    new_status = request.form['status']
    database.update_request_status(request_id, new_status)
    flash(f'Anfrage #{request_id} wurde auf {new_status} aktualisiert.')
    return redirect(url_for('admin_panel'))

@app.route('/admin/update_status/<int:ticket_id>/<string:new_status>')
@login_required
def update_ticket_status(ticket_id, new_status):
    """Status-Update für das Ticketing-System (admin_tickets.html)."""
    if current_user.role != 'admin':
        return "Nicht autorisiert", 403
    
    database.update_request_status(ticket_id, new_status)
    flash(f'Ticket #{ticket_id} Status auf {new_status} gesetzt.')
    return redirect(url_for('admin_tickets'))

@app.route('/admin/tickets')
@login_required
def admin_tickets():
    """Detailansicht aller Tickets."""
    if current_user.role != 'admin':
        return "Zugriff verweigert", 403
    tickets = database.get_all_requests()
    return render_template('admin_tickets.html', tickets=tickets)

# --- IT-Inventory / CMDB ---

@app.route('/admin/cmdb', methods=['GET', 'POST'])
@login_required
def admin_cmdb():
    """Verwaltung des IT-Inventars."""
    if current_user.role != 'admin':
        flash('Nur Administratoren haben Zugriff.')
        return redirect(url_for('index'))

    if request.method == 'POST':
        tag = request.form['asset_tag']
        name = request.form['item_name']
        sn = request.form['serial_number']
        user = request.form['assigned_to']
        status = request.form['status']
        loc = request.form['location']
        
        if database.add_inventory_item(tag, name, sn, user, status, loc):
            flash('Gegenstand erfolgreich hinzugefügt.')
        else:
            flash('Fehler: Asset Tag existiert bereits!')

    inventory_items = database.get_inventory()
    return render_template('cmdb.html', items=inventory_items)

# --- Excel Export ---

@app.route('/admin/export/tickets')
@login_required
def export_tickets_excel():
    """Exportiert alle Tickets in eine Excel-Datei."""
    if current_user.role != 'admin':
        return "Zugriff verweigert", 403
    
    tickets = database.get_all_requests()
    df = pd.DataFrame(tickets)
    df.columns = ['Ticket-ID', 'Service-Code', 'Mitarbeiter', 'Abteilung', 'Status', 'Grund', 'Erstellungsdatum']
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='IT-Tickets')
    
    output.seek(0)
    return send_file(output, 
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True, 
                     download_name='IT_Tickets_Report.xlsx')

# --- Service Management ---

@app.route('/admin/add', methods=['GET', 'POST'])
@login_required
def add_service_form():
    """Erstellung neuer Services."""
    if current_user.role != 'admin':
        return "Zugriff verweigert", 403
    
    if request.method == 'POST':
        service = {
            'id': request.form['id'],
            'name': request.form['name'],
            'category': request.form['category'],
            'availability': request.form['availability'],
            'description_business': request.form['description_business'],
            'description_technical': request.form['description_technical'],
            'sla': request.form['sla'],
            'costs': request.form['costs']
        }
        database.add_service(service)
        flash('Service erfolgreich hinzugefügt.')
        return redirect(url_for('index'))
    return render_template('add_service.html')

if __name__ == '__main__':
    app.run(debug=True)