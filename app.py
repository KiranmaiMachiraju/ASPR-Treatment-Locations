from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3 
from openai_helper import call_openai_chat

app = Flask(__name__)
DB_PATH = 'aspr_data.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # rows behave like dicts
    return conn

@app.route('/api/states')
def get_states():
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT State as state,
               AVG(Latitude) as lat,
               AVG(Longitude) as lng
        FROM locations
        WHERE Latitude IS NOT NULL AND Longitude IS NOT NULL
        GROUP BY State
    """).fetchall()
    conn.close()

    states = [
        {"state": row["state"], "lat": row["lat"], "lng": row["lng"]}
        for row in rows
    ]
    return jsonify(states)


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
            return redirect(url_for('customer_start'))
    return render_template('choose_role.html')

@app.route('/provider/start', methods=['GET', 'POST'])
def provider_start():
    conn = get_db_connection()
    states = [row['state'] for row in conn.execute(
        'SELECT DISTINCT state FROM locations WHERE state IS NOT NULL ORDER BY state')]
    conn.close()

    return render_template('provider_start.html',
                           states=states,
                           vaccinations=vaccinations_list)

# UPDATED: customer_start now renders test_maps.html with states for map markers
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
    
    # Render the map page here instead of the old customer_start.html
    return render_template('test_maps.html', states=states)

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

@app.route('/test_maps')
def test_maps():
    return render_template('test_maps.html')

vaccinations_list = [
    {'field': 'Is_Flu', 'label': 'Flu Vaccine'},
    {'field': 'Is_COVID-19', 'label': 'COVID-19 Vaccine'},
    {'field': 'Has_USG_Product', 'label': 'USG Product Available'},
    {'field': 'Has_Commercial_Product', 'label': 'Commercial Product Available'},
    {'field': 'Has_Paxlovid', 'label': 'Paxlovid'},
    {'field': 'Has_Commercial_Paxlovid', 'label': 'Commercial Paxlovid'},
    {'field': 'Has_USG_Paxlovid', 'label': 'USG Paxlovid'},
    {'field': 'Has_Lagevrio', 'label': 'Lagevrio'},
    {'field': 'Has_Commercial_Lagevrio', 'label': 'Commercial Lagevrio'},
    {'field': 'Has_USG_Lagevrio', 'label': 'USG Lagevrio'},
    {'field': 'Has_Veklury', 'label': 'Veklury'},
    {'field': 'Has_Oseltamivir_Generic', 'label': 'Oseltamivir Generic'},
    {'field': 'Has_Oseltamivir_Suspension', 'label': 'Oseltamivir Suspension'},
    {'field': 'Has_Oseltamivir_Tamiflu', 'label': 'Oseltamivir Tamiflu'},
    {'field': 'Has_Baloxavir', 'label': 'Baloxavir'},
    {'field': 'Has_Zanamivir', 'label': 'Zanamivir'},
    {'field': 'Has_Peramivir', 'label': 'Peramivir'}
]

@app.route('/provider/vaccinations', methods=['GET', 'POST'])
def provider_vaccinations():
    conn = get_db_connection()

    # Fetch filter options
    states = [row['state'] for row in conn.execute(
        'SELECT DISTINCT state FROM locations WHERE state IS NOT NULL ORDER BY state')]

    cities = []
    zips = []

    selected_vaccinations = []
    selected_state = request.form.get('state') if request.method == 'POST' else None
    selected_city = request.form.get('city') if request.method == 'POST' else None
    selected_zip = request.form.get('zip') if request.method == 'POST' else None

    # Load cities and zips based on selected state
    if selected_state:
        cities = [row['city'] for row in conn.execute(
            'SELECT DISTINCT city FROM locations WHERE state = ? AND city IS NOT NULL ORDER BY city', (selected_state,))]

    if selected_city:
        zips = [row['zip'] for row in conn.execute(
            'SELECT DISTINCT zip FROM locations WHERE city = ? AND zip IS NOT NULL ORDER BY zip', (selected_city,))]

    providers = []

    if request.method == 'POST':
        selected_vaccinations = request.form.getlist('vaccinations')
        where_clauses = []
        params = []

        if selected_vaccinations:
            where_clauses.append('(' + ' OR '.join([f'"{vacc}" = 1' for vacc in selected_vaccinations]) + ')')

        if selected_state:
            where_clauses.append('state = ?')
            params.append(selected_state)

        if selected_city:
            where_clauses.append('city = ?')
            params.append(selected_city)

        if selected_zip:
            where_clauses.append('zip = ?')
            params.append(selected_zip)

        query = "SELECT * FROM locations"
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        providers = conn.execute(query, params).fetchall()

    conn.close()

    return render_template('provider_vaccinations.html',
                           vaccinations=vaccinations_list,
                           selected_vaccinations=selected_vaccinations,
                           providers=providers,
                           states=states,
                           cities=cities,
                           zips=zips,
                           selected_state=selected_state,
                           selected_city=selected_city,
                           selected_zip=selected_zip)


@app.route("/chatbot")
def chatbot():
    return render_template("chat_bot.html")


@app.route("/chatbot/message", methods=["POST"])
def chatbot_message():
    data = request.get_json()
    user_message = data.get("message")
    bot_response = call_openai_chat(user_message)
    return jsonify({"response": bot_response})

if __name__ == '__main__':
    app.run(debug=True)
