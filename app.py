import os
import sqlite3
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import database
from models import User

# Laden der Umgebungsvariablen aus der .env Datei
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'fallback-dev-key')

# Konfiguration von Flask-Login für die Sitzungsverwaltung
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    """Lädt den Benutzer aus der Datenbank anhand der ID."""
    conn = sqlite3.connect(database.DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, username, role, fullname, department FROM users WHERE id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return User(row[0], row[1], row[2], row[3], row[4])
    return None

# Initialisierung der Datenbanktabellen beim Start
database.init_db()

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Verarbeitet die Anmeldung der Benutzer."""
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

@app.route('/logout')
@login_required
def logout():
    """Loggt den aktuellen Benutzer aus."""
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    """Startseite mit Anzeige des Service-Katalogs."""
    category = request.args.get('category')
    services = database.get_services(category)
    return render_template('index.html', user=current_user, services=services)

@app.route('/request/<service_id>')
@login_required
def show_request_form(service_id):
    """Zeigt das Formular für eine neue Service-Anfrage an."""
    return render_template('service_request.html', service_id=service_id, user=current_user)

@app.route('/request', methods=['POST'])
@login_required
def request_service():
    """Speichert die vom Benutzer gesendete Service-Anfrage."""
    service_id = request.form['service_id']
    reason = request.form.get('reason', '')
    
    # Speichern der Anfrage in der Datenbank
    database.add_request(service_id, current_user.fullname, current_user.department, reason)
    
    return redirect(url_for('requests_list'))

@app.route('/requests')
@login_required
def requests_list():
    """Zeigt dem Benutzer seine eigenen gestellten Anfragen."""
    reqs = database.get_requests(user_name=current_user.fullname)
    return render_template('requests.html', requests=reqs)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registrierung neuer Benutzer. 'admin' wird automatisch Admin-Rolle zugewiesen."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        fullname = request.form['fullname']
        department = request.form['department']
        
        if database.get_user(username):
            flash('Benutzername existiert bereits.')
            return redirect(url_for('register'))
        
        # Automatische Zuweisung der Admin-Rolle für den Benutzernamen 'admin'
        role = 'admin' if username.lower() == 'admin' else 'user'
        
        database.add_user(username, password, role, fullname, department)
        flash('Registrierung erfolgreich. Bitte loggen Sie sich ein.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/admin/add', methods=['GET', 'POST'])
@login_required
def add_service_form():
    """Ermöglicht Administratoren das Hinzufügen neuer Services."""
    if current_user.role != 'admin':
        flash('Zugriff verweigert. Nur für Administratoren.')
        return redirect(url_for('index'))
    
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
        return redirect(url_for('index'))
    return render_template('add_service.html')

@app.route('/admin')
@login_required
def admin_panel():
    """Übersicht aller Anfragen für Administratoren."""
    if current_user.role != 'admin':
        return "Zugriff verweigert", 403
    requests_all = database.get_all_requests()
    return render_template('admin.html', requests=requests_all)

@app.route('/admin/update/<int:request_id>', methods=['POST'])
@login_required
def admin_update_request(request_id):
    """Aktualisiert den Status einer Anfrage durch den Administrator."""
    if current_user.role != 'admin':
        return "Zugriff verweigert", 403
    new_status = request.form['status']
    database.update_request_status(request_id, new_status)
    return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    # Startet die Anwendung im Debug-Modus
    app.run(debug=True)