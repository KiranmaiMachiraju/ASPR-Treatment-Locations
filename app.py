from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import os
from dotenv import load_dotenv
import openai

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from environment variables
openai.api_key = os.getenv('OPENAI_API_KEY')

app = Flask(__name__)
DB_PATH = 'aspr_data.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/chatbot')
def chatbot_page():
    return render_template('chatbot.html')


# ---------------- API ----------------
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

    states = [{"state": row["state"], "lat": row["lat"], "lng": row["lng"]} for row in rows]
    return jsonify(states)

# ---------------- CHATBOT API ----------------
@app.route('/api/chatbot', methods=['GET'])
def chatbot():
    user_query = request.args.get('question')
    if not user_query:
        return jsonify({
            'answer': "Please provide a valid query.",
            'locations': []
        })

    conn = get_db_connection()
    query = """
        SELECT Provider_Name, Address_1, Address_2, City, State, Zip, Public_Phone, Appointment_URL
        FROM locations
        WHERE Provider_Name LIKE ? OR Address_1 LIKE ? OR City LIKE ?
    """
    params = ('%' + user_query + '%', '%' + user_query + '%', '%' + user_query + '%')
    rows = conn.execute(query, params).fetchall()

    locations = [
        {
            'Provider_Name': row['Provider_Name'],
            'Address_1': row['Address_1'],
            'Address_2': row['Address_2'],
            'City': row['City'],
            'State': row['State'],
            'Zip': row['Zip'],
            'Public_Phone': row['Public_Phone'],
            'Appointment_URL': row['Appointment_URL']
        }
        for row in rows
    ]
    conn.close()

    prompt = f"User asked: {user_query}. Provide a helpful, concise answer."
    if locations:
        prompt += f"\nThere are {len(locations)} matching locations in the database."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant providing info about healthcare locations."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7,
        )
        answer = response['choices'][0]['message']['content'].strip()
    except Exception as e:
        answer = "Sorry, I couldn't process your request at this time."

    return jsonify({
        'answer': answer,
        'locations': locations
    })


# ---------------- HOME ----------------
@app.route('/')
def home():
    return render_template('home.html')

# ---------------- CHOOSE ROLE ----------------
@app.route('/choose_role', methods=['GET', 'POST'])
def choose_role():
    if request.method == 'POST':
        role = request.form.get('role')
        if role == 'provider':
            return redirect(url_for('provider_start'))
        elif role == 'customer':
            return redirect(url_for('customer_start'))
    return render_template('choose_role.html')

# ---------------- PROVIDER START ----------------
@app.route('/provider/start', methods=['GET', 'POST'])
def provider_start():
    conn = get_db_connection()

    # States for dropdown
    states = [row['state'] for row in conn.execute(
        'SELECT DISTINCT state FROM locations WHERE state IS NOT NULL ORDER BY state')]

    # --- KPIs ---
    kpi_query = """
        SELECT
            COUNT(*) AS total_providers,
            SUM(Is_PAP_Site) AS total_pap_sites,
            SUM(Prescribing_Services_Available) AS total_prescribers,
            SUM(Has_Paxlovid) AS total_paxlovid,
            SUM(Has_Lagevrio) AS total_lagevrio,
            SUM(Has_Veklury) AS total_veklury,
            SUM(Is_Flu) AS total_flu,
            SUM("Is_COVID-19") AS total_covid
        FROM locations
    """
    kpis = conn.execute(kpi_query).fetchone()

    # --- Chart data ---
    # Providers per state
    state_count_rows = conn.execute("""
        SELECT state, COUNT(*) AS provider_count
        FROM locations
        GROUP BY state
        ORDER BY provider_count DESC
    """).fetchall()
    states_chart = [row['state'] for row in state_count_rows]
    providers_chart = [row['provider_count'] for row in state_count_rows]

    # Medication availability (Paxlovid, Lagevrio, Veklury)
    med_rows = conn.execute("""
        SELECT
            SUM(Has_Paxlovid) AS paxlovid,
            SUM(Has_Lagevrio) AS lagevrio,
            SUM(Has_Veklury) AS veklury
        FROM locations
    """).fetchone()
    conn.close()

    if request.method == 'POST':
        selected_state = request.form.get('state')
        if selected_state:
            return redirect(url_for('provider', state=selected_state))

    return render_template(
        'provider_start.html',
        states=states,
        kpis=kpis,
        states_chart=states_chart,
        providers_chart=providers_chart,
        med_rows=med_rows
    )


# ---------------- PROVIDER ----------------
@app.route('/provider')
def provider():
    selected_state = request.args.get('state')

    if not selected_state:
        return redirect(url_for('provider_start'))

    conn = get_db_connection()

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

    # --- KPIs ---
    stats_query = """
        SELECT
            COUNT(*) AS total_providers,
            SUM(Is_Flu) AS total_flu,
            SUM("Is_COVID-19") AS total_covid,
            SUM(Has_USG_Product) AS total_usg_product,
            SUM(Has_Commercial_Product) AS total_commercial_product,
            SUM(Has_Paxlovid) AS total_paxlovid,
            SUM(Has_Commercial_Paxlovid) AS total_commercial_paxlovid,
            SUM(Has_USG_Paxlovid) AS total_usg_paxlovid,
            SUM(Has_Lagevrio) AS total_lagevrio,
            SUM(Has_Commercial_Lagevrio) AS total_commercial_lagevrio,
            SUM(Has_USG_Lagevrio) AS total_usg_lagevrio,
            SUM(Has_Veklury) AS total_veklury,
            SUM(Has_Oseltamivir_Generic) AS total_oseltamivir_generic,
            SUM(Has_Oseltamivir_Suspension) AS total_oseltamivir_suspension,
            SUM(Has_Oseltamivir_Tamiflu) AS total_oseltamivir_tamiflu,
            SUM(Has_Baloxavir) AS total_baloxavir,
            SUM(Has_Zanamivir) AS total_zanamivir,
            SUM(Has_Peramivir) AS total_peramivir
        FROM locations
        WHERE state = ?
    """
    stats = conn.execute(stats_query, (selected_state,)).fetchone()

    conn.close()

    filters = {'state': selected_state, 'city': selected_city, 'zip': selected_zip}

    return render_template('provider.html',
                           states=states,
                           cities=cities,
                           providers=providers,
                           filters=filters,
                           stats=stats)

# ---------------- CUSTOMER START ----------------
@app.route('/customer/start', methods=['GET', 'POST'])
def customer_start():
    conn = get_db_connection()
    states = [row['State'] for row in conn.execute(
        'SELECT DISTINCT State FROM locations WHERE State IS NOT NULL ORDER BY State')]
    conn.close()

    if request.method == 'POST':
        selected_state = request.form.get('state')
        if selected_state:
            return redirect(url_for('customer', state=selected_state))
    
    return render_template('test_maps.html', states=states)


# ---------------- CUSTOMER VIEW ----------------
@app.route('/customer')
def customer():
    selected_state = request.args.get('state')
    if not selected_state:
        return redirect(url_for('customer_start'))

    conn = get_db_connection()
    states = [row['State'] for row in conn.execute(
        'SELECT DISTINCT State FROM locations WHERE State IS NOT NULL ORDER BY State')]
    
    selected_city = request.args.get('city')
    selected_zip = request.args.get('zip')

    query = "SELECT * FROM locations WHERE State = ?"
    params = [selected_state]
    if selected_city:
        query += " AND City = ?"
        params.append(selected_city)
    if selected_zip:
        query += " AND Zip = ?"
        params.append(selected_zip)

    providers = conn.execute(query, params).fetchall()
    cities = [row['City'] for row in conn.execute(
        "SELECT DISTINCT City FROM locations WHERE State = ? AND City IS NOT NULL ORDER BY City", (selected_state,))]

    conn.close()
    filters = {'state': selected_state, 'city': selected_city, 'zip': selected_zip}

    return render_template('customer.html',
                           states=states,
                           cities=cities,
                           providers=providers,
                           filters=filters)

if __name__ == '__main__':
    app.run(debug=True)
