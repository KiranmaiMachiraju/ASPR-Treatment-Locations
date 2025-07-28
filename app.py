from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DB_PATH = 'aspr_data.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # rows behave like dicts
    return conn

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/choose_role', methods=['GET', 'POST'])
def choose_role():
    if request.method == 'POST':
        role = request.form.get('role')
        if role == 'provider':
            return redirect(url_for('provider'))
        elif role == 'customer':
            return redirect(url_for('customer'))
    return render_template('choose_role.html')

@app.route('/provider/start', methods=['GET', 'POST'])
def provider_start():
    conn = get_db_connection()
    states = [row['state'] for row in conn.execute(
        'SELECT DISTINCT state FROM locations WHERE state IS NOT NULL ORDER BY state')]
    conn.close()

    if request.method == 'POST':
        selected_state = request.form.get('state')
        if selected_state:
            return redirect(url_for('provider', state=selected_state))
    
    return render_template('provider_start.html', states=states)

@app.route('/customer/start', methods=['GET', 'POST'])
def customer_start():
    conn = get_db_connection()
    states = [row['state'] for row in conn.execute(
        'SELECT DISTINCT state FROM locations WHERE state IS NOT NULL ORDER BY state')]
    conn.close()

    if request.method == 'POST':
        selected_state = request.form.get('state')
        if selected_state:
            return redirect(url_for('customer', state=selected_state))
    
    return render_template('customer_start.html', states=states)

@app.route('/provider')
def provider():
    selected_state = request.args.get('state')

    if not selected_state:
        return redirect(url_for('provider_start'))  # Don't load anything without a state

    conn = get_db_connection()

    # Get dropdown data
    states = [row['state'] for row in conn.execute(
        'SELECT DISTINCT state FROM locations WHERE state IS NOT NULL ORDER BY state')]

    selected_city = request.args.get('city')
    selected_zip = request.args.get('zip')

    query = "SELECT * FROM locations WHERE state = ?"
    params = [selected_state]

    if selected_city:
        query += " AND city = ?"
        params.append(selected_city)
    if selected_zip:
        query += " AND zip = ?"
        params.append(selected_zip)

    providers = conn.execute(query, params).fetchall()

    # City dropdown
    cities = [row['city'] for row in conn.execute(
        "SELECT DISTINCT city FROM locations WHERE state = ? AND city IS NOT NULL ORDER BY city", (selected_state,))]

    conn.close()

    filters = {'state': selected_state, 'city': selected_city, 'zip': selected_zip}

    return render_template('provider.html',
                           states=states,
                           cities=cities,
                           providers=providers,
                           filters=filters)


@app.route('/customer')
def customer():
    selected_state = request.args.get('state')

    if not selected_state:
        return redirect(url_for('customer_start'))  # Don't load anything without a state

    conn = get_db_connection()

    # Get dropdown data
    states = [row['state'] for row in conn.execute(
        'SELECT DISTINCT state FROM locations WHERE state IS NOT NULL ORDER BY state')]

    selected_city = request.args.get('city')
    selected_zip = request.args.get('zip')

    query = "SELECT * FROM locations WHERE state = ?"
    params = [selected_state]

    if selected_city:
        query += " AND city = ?"
        params.append(selected_city)
    if selected_zip:
        query += " AND zip = ?"
        params.append(selected_zip)

    providers = conn.execute(query, params).fetchall()

    # City dropdown
    cities = [row['city'] for row in conn.execute(
        "SELECT DISTINCT city FROM locations WHERE state = ? AND city IS NOT NULL ORDER BY city", (selected_state,))]

    conn.close()

    filters = {'state': selected_state, 'city': selected_city, 'zip': selected_zip}

    return render_template('customer.html',
                           states=states,
                           cities=cities,
                           providers=providers,
                           filters=filters)

if __name__ == '__main__':
    app.run(debug=True)
