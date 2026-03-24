import os
import sqlite3
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash
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
            return redirect(url_for('index'))
        else:
            flash('Ungültiger Benutzername oder Passwort')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Benutzerregistrierung (Admin-Rolle wird bei Username 'admin' vergeben)."""
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
    """Zeigt das Anfrageformular für einen bestimmten Service."""
    all_s = database.get_services()
    service = next((s for s in all_s if s['id'] == service_id), None)
    return render_template('service_request.html', service=service, user=current_user)

@app.route('/request', methods=['POST'])
@login_required
def request_service():
    """Speichert eine neue Service-Anfrage in der Datenbank."""
    service_id = request.form['service_id']
    reason = request.form.get('reason', '')
    
    database.add_request(service_id, current_user.fullname, current_user.department, reason)
    flash('Ihre Anfrage wurde erfolgreich gesendet.')
    return redirect(url_for('requests_list'))

@app.route('/requests')
@login_required
def requests_list():
    """Anzeige der eigenen Anfragen des Benutzers."""
    reqs = database.get_requests(user_name=current_user.fullname)
    return render_template('requests.html', requests=reqs)

# --- Administration (Admin) ---

@app.route('/admin')
@login_required
def admin_panel():
    """Panel für Administratoren zur Verwaltung aller Anfragen."""
    if current_user.role != 'admin':
        flash('Zugriff verweigert.')
        return redirect(url_for('index'))
    
    requests_all = database.get_all_requests()
    return render_template('admin.html', requests=requests_all)

@app.route('/admin/add', methods=['GET', 'POST'])
@login_required
def add_service_form():
    """Erstellung neuer Services durch den Administrator."""
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

@app.route('/admin/update/<int:request_id>', methods=['POST'])
@login_required
def admin_update_request(request_id):
    """Status-Update einer Anfrage (Genehmigen/Ablehnen)."""
    if current_user.role != 'admin':
        return "Zugriff verweigert", 403
    
    new_status = request.form['status']
    database.update_request_status(request_id, new_status)
    flash(f'Anfrage #{request_id} wurde aktualisiert.')
    return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    app.run(debug=True)