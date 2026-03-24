from flask import Flask, render_template, request, redirect, url_for
import database

app = Flask(__name__)

database.init_db()

current_user = {
    'name': 'Sarah Schmidt',
    'dept': 'Vertrieb'
}

@app.route('/')
def index():
    category = request.args.get('category')
    services = database.get_services(category)
    return render_template('index.html', user=current_user, services=services)

@app.route('/request', methods=['POST'])
def request_service():
    service_id = request.form['service_id']
    database.add_request(service_id, current_user['name'], current_user['dept'])
    return redirect(url_for('requests_list'))

@app.route('/requests')
def requests_list():
    reqs = database.get_requests(user_name=current_user['name'])
    return render_template('requests.html', requests=reqs)

@app.route('/admin/add', methods=['GET', 'POST'])
def add_service_form():
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

if __name__ == '__main__':
    app.run(debug=True)