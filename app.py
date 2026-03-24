import os
import sqlite3
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import database
from models import User

# Load environment variables (for local development)
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'fallback-dev-key')

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect(database.DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, username, role, fullname, department FROM users WHERE id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return User(row[0], row[1], row[2], row[3], row[4])
    return None

# Initialize database (creates tables if needed)
database.init_db()

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
        else:
            flash('Invalid username or password')
    return render_template('login.html')

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
    return render_template('service_request.html', service_id=service_id, user=current_user)

@app.route('/request', methods=['POST'])
@login_required
def request_service():
    service_id = request.form['service_id']
    database.add_request(service_id, current_user.fullname, current_user.department)
    return redirect(url_for('requests_list'))

@app.route('/requests')
@login_required
def requests_list():
    reqs = database.get_requests(user_name=current_user.fullname)
    return render_template('requests.html', requests=reqs)

@app.route('/admin/add', methods=['GET', 'POST'])
@login_required
def add_service_form():
    if current_user.role != 'admin':
        flash('Access denied. Admin only.')
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
    if current_user.role != 'admin':
        return "Access denied", 403
    requests = database.get_all_requests()
    return render_template('admin.html', requests=requests)

@app.route('/admin/update/<int:request_id>', methods=['POST'])
@login_required
def admin_update_request(request_id):
    if current_user.role != 'admin':
        return "Access denied", 403
    new_status = request.form['status']
    database.update_request_status(request_id, new_status)
    return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    app.run(debug=True)