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

@app.route('/provider', methods=['GET', 'POST'])
def provider():
    conn = get_db_connection()
    # Fetch distinct states for dropdown
    states = [row['State'] for row in conn.execute('SELECT DISTINCT State FROM locations ORDER BY State')]
    
    selected_state = request.form.get('state')
    selected_city = request.form.get('city')
    selected_zip = request.form.get('zip')

    # Build base query and params list
    query = "SELECT * FROM locations WHERE 1=1"
    params = []

    if selected_state:
        query += " AND State = ?"
        params.append(selected_state)
    if selected_city:
        query += " AND City = ?"
        params.append(selected_city)
    if selected_zip:
        query += " AND Zip = ?"
        params.append(selected_zip)

    results = conn.execute(query, params).fetchall()

    # Fetch cities for selected state
    cities = []
    if selected_state:
        cities = [row['City'] for row in conn.execute("SELECT DISTINCT City FROM locations WHERE State = ? ORDER BY City", (selected_state,))]

    conn.close()

    return render_template('provider.html',
                           states=states,
                           cities=cities,
                           results=results,
                           selected_state=selected_state,
                           selected_city=selected_city,
                           selected_zip=selected_zip)

@app.route('/customer', methods=['GET', 'POST'])
def customer():
    # For now, same as provider, but you can customize this view later
    conn = get_db_connection()
    states = [row['State'] for row in conn.execute('SELECT DISTINCT State FROM locations ORDER BY State')]
    
    selected_state = request.form.get('state')
    selected_city = request.form.get('city')
    selected_zip = request.form.get('zip')

    query = "SELECT * FROM locations WHERE 1=1"
    params = []

    if selected_state:
        query += " AND State = ?"
        params.append(selected_state)
    if selected_city:
        query += " AND City = ?"
        params.append(selected_city)
    if selected_zip:
        query += " AND Zip = ?"
        params.append(selected_zip)

    results = conn.execute(query, params).fetchall()

    cities = []
    if selected_state:
        cities = [row['City'] for row in conn.execute("SELECT DISTINCT City FROM locations WHERE State = ? ORDER BY City", (selected_state,))]

    conn.close()

    return render_template('customer.html',
                           states=states,
                           cities=cities,
                           results=results,
                           selected_state=selected_state,
                           selected_city=selected_city,
                           selected_zip=selected_zip)

if __name__ == '__main__':
    app.run(debug=True)
