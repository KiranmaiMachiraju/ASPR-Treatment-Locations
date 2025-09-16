from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from environment variables
client = OpenAI(api_key=os.getenv("API_KEY"))

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

def generate_sql_from_prompt(prompt):
    system_message = (
        "You are a helpful assistant that translates natural language questions "
        "into SQL queries for a SQLite table named 'locations'.\n"
        "ONLY use the exact column names listed below — do not infer or rename anything.\n"
        "Respond ONLY with a valid SQL query. Do not include explanations.\n\n"
        "Available columns:\n"
        "- Provider_Name\n"
        "- Address_1\n"
        "- Address_2\n"
        "- City\n"
        "- State\n"
        "- Zip\n"
        "- Public_Phone\n"
        "- Latitude\n"
        "- Longitude\n"
        "- Geopoint\n"
        "- Last_Report_Date\n"
        "- Is_PAP_Site\n"
        "- Prescribing_Services_Available\n"
        "- Appointment_URL\n"
        "- Home_Delivery\n"
        "- Is_ICATT_Site\n"
        "- Has_USG_Product\n"
        "- Has_Commercial_Product\n"
        "- Has_Paxlovid\n"
        "- Has_Commercial_Paxlovid\n"
        "- Has_USG_Paxlovid\n"
        "- Has_Lagevrio\n"
        "- Has_Commercial_Lagevrio\n"
        "- Has_USG_Lagevrio\n"
        "- Has_Veklury\n"
        "- Has_Oseltamivir_Generic\n"
        "- Has_Oseltamivir_Suspension\n"
        "- Has_Oseltamivir_Tamiflu\n"
        "- Has_Baloxavir\n"
        "- Has_Zanamivir\n"
        "- Has_Peramivir\n"
        "- Grantee_Code\n"
        "- Is_Flu\n"
        "- Is_COVID19\n"
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content.strip()


@app.route('/api/chatbot', methods=['GET'])
def chatbot():
    user_query = request.args.get('question', '').strip()

    if not user_query:
        return jsonify({'answer': "Please enter a valid question."})

    try:
        sql = generate_sql_from_prompt(user_query)
        print(f"Generated SQL:\n{sql}")

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(sql)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()

        if not rows:
            return jsonify({'answer': "Sorry, I couldn't find any matching treatment locations."})

        # Format up to 5 results for display
        results = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            meds = []
            for med_col in ['Has_Paxlovid', 'Has_Lagevrio', 'Has_Veklury']:
                if row_dict.get(med_col):
                    meds.append(med_col.replace('Has_', ''))
            meds_str = ", ".join(meds) if meds else "No specific medications listed"

            answer_part = (
                f"Provider: {row_dict.get('Provider_Name', 'N/A')}\n"
                f"Address: {row_dict.get('Address_1', '')} {row_dict.get('Address_2', '')}, "
                f"{row_dict.get('City', '')}, {row_dict.get('State', '')} {row_dict.get('Zip', '')}\n"
                f"Phone: {row_dict.get('Public_Phone', 'N/A')}\n"
                f"Medications available: {meds_str}\n"
            )
            results.append(answer_part)

        full_answer = f"I found {len(rows)} matching treatment locations:\n\n" + "\n---\n".join(results)
        return jsonify({'answer': full_answer})

    except sqlite3.Error as e:
        return jsonify({'answer': f"Database error occurred: {e}"})
    except Exception as e:
        return jsonify({'answer': f"An error occurred: {e}"})


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
            SUM("Is_COVID19") AS total_covid
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

    # States for dropdown
    states = [row['state'] for row in conn.execute(
        'SELECT DISTINCT state FROM locations WHERE state IS NOT NULL ORDER BY state')]

    selected_city = request.args.get('city')
    selected_zip = request.args.get('zip')

    # Base query
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
        "SELECT DISTINCT city FROM locations WHERE state = ? AND city IS NOT NULL ORDER BY city",
        (selected_state,)
    )]

    # --- KPIs ---
    stats_query = """
        SELECT
            COUNT(*) AS total_providers,
            SUM(Is_Flu) AS total_flu,
            SUM("Is_COVID19") AS total_covid,
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
    stats_row = conn.execute(stats_query, (selected_state,)).fetchone()
    conn.close()

    # Convert stats into dict for easier Jinja use
    stats = dict(stats_row)

    filters = {
        'state': selected_state,
        'city': selected_city,
        'zip': selected_zip
    }

    return render_template(
        'provider.html',
        states=states,
        cities=cities,
        providers=providers,
        filters=filters,
        stats=stats
    )

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
