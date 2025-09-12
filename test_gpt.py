import sqlite3
from openai import OpenAI

# Set your API key (or use environment variables)
client = OpenAI(api_key="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")

# Connect to your SQLite database
conn = sqlite3.connect("aspr_data.db")  # Replace with your actual file
cursor = conn.cursor()

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
        "- Is_COVID-19\n"
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content.strip()


def run_query(sql_query):
    try:
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        return f"Error running query: {e}"

def main():
    user_input = input("Ask something about the treatment locations:\n> ")

    sql = generate_sql_from_prompt(user_input)
    print(f"\nGenerated SQL:\n{sql}")

    result = run_query(sql)
    print(f"\nQuery Result:\n{result}")

if __name__ == "__main__":
    main()

