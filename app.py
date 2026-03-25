import os
import sqlite3
import io
import pandas as pd
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import database
from models import User

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'mein-it-portal-geheimnis-2026')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    """Lädt den Benutzer aus der Datenbank für Flask-Login."""
    try:
        conn = sqlite3.connect(database.DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, username, role, fullname, department FROM users WHERE id=?", (user_id,))
        row = c.fetchone()
        conn.close()
        if row:
            return User(row[0], row[1], row[2], row[3], row[4])
    except:
        return None
    return None

# Initialisiert die Datenbank beim Start
database.init_db()

@app.route('/health')
def health_check():
    """Health Check für Render Auto-Deploy."""
    return "OK", 200

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_data = database.get_user(username)
        if user_data and user_data['password'] == password:
            user = User(user_data['id'], user_data['username'], user_data['role'],
                        user_data['fullname'], user_data['department'])
            login_user(user)
            return redirect(url_for('index'))
        flash('Ungültiger Benutzername oder Passwort')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        fullname = request.form['fullname']
        department = request.form['department']
        if database.get_user(username):
            flash('Benutzername existiert bereits.')
            return redirect(url_for('register'))
        # Erster User oder 'admin' wird Admin
        role = 'admin' if username.lower() == 'admin' else 'user'
        database.add_user(username, password, role, fullname, department)
        flash('Registrierung erfolgreich. Bitte einloggen.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    category = request.args.get('category')
    services = database.get_services(category)
    return render_template('index.html', user=current_user, services=services)

@app.route('/request/<service_id>')
@login_required
def show_request_form(service_id):
    service = database.get_service(service_id)
    return render_template('service_request.html', service=service, user=current_user)

@app.route('/request', methods=['POST'])
@login_required
def request_service():
    service_id = request.form['service_id']
    reason = request.form.get('reason', '')
    # Nutzt fullname des aktuellen Users für das Ticket
    database.add_request(service_id, current_user.fullname, current_user.department, reason)
    flash('Ihre Anfrage wurde erfolgreich gesendet.')
    return redirect(url_for('requests_list'))

@app.route('/requests')
@login_required
def requests_list():
    reqs = database.get_requests(user_name=current_user.fullname)
    return render_template('requests.html', requests=reqs)

@app.route('/admin')
@login_required
def admin_panel():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    try:
        stats = database.get_ticket_stats()
        inv_count = database.get_inventory_count()
        requests_all = database.get_all_requests()
        return render_template('admin.html', requests=requests_all, stats=stats, inv_count=inv_count)
    except Exception as e:
        return f"Fehler im Admin-Bereich: {str(e)}", 500

@app.route('/admin/update/<int:request_id>', methods=['POST'])
@login_required
def admin_update_request(request_id):
    if current_user.role == 'admin':
        new_status = request.form['status']
        database.update_request_status(request_id, new_status)
    return redirect(url_for('admin_panel'))

@app.route('/admin/cmdb', methods=['GET', 'POST'])
@login_required
def admin_cmdb():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    if request.method == 'POST':
        success = database.add_inventory_item(
            request.form['asset_tag'], request.form['item_name'],
            request.form['serial_number'], request.form['assigned_to'],
            request.form['status'], request.form['location']
        )
        if success:
            flash('Inventar erfolgreich aktualisiert.')
        else:
            flash('Fehler: Asset Tag existiert bereits!')
        return redirect(url_for('admin_cmdb'))
    
    items = database.get_inventory()
    return render_template('cmdb.html', items=items)

@app.route('/admin/add_service', methods=['GET', 'POST'])
@login_required
def add_service_form():
    if current_user.role != 'admin':
        return redirect(url_for('index'))
    if request.method == 'POST':
        service_data = {
            'id': request.form['id'],
            'name': request.form['name'],
            'category': request.form['category'],
            'availability': request.form['availability'],
            'description_business': request.form['description_business'],
            'description_technical': request.form['description_technical'],
            'sla': request.form['sla'],
            'costs': request.form['costs']
        }
        database.add_service(service_data)
        flash('Service erfolgreich zum Katalog hinzugefügt.')
        return redirect(url_for('index'))
    return render_template('add_service.html')

@app.route('/admin/export/tickets')
@login_required
def export_tickets_excel():
    if current_user.role != 'admin':
        return "Zugriff verweigert", 403
    tickets = database.get_all_requests()
    if not tickets:
        flash("Keine Daten zum Exportieren vorhanden.")
        return redirect(url_for('admin_panel'))
    
    try:
        df = pd.DataFrame(tickets)
        output = io.BytesIO()
        # Verwendet openpyxl für modernen Excel-Export
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='IT_Tickets')
        output.seek(0)
        return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                         as_attachment=True, download_name='IT_Service_Report_2026.xlsx')
    except Exception as e:
        flash(f"Excel-Export fehlgeschlagen: {str(e)}")
        return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    # Lokal auf Port 5000 ausführen
    app.run(host='0.0.0.0', port=5000, debug=True)