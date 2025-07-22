import pandas as pd
import sqlite3

csv_path = 'data/ASPR_Treatments_Locator.csv'  # or 'data/aspr_data.csv' if inside data folder
db_path = 'aspr_data.db'

print("Loading CSV file...")
df = pd.read_csv(csv_path)

print("Cleaning column names...")
# Optional: strip spaces from column names for easier querying
df.columns = [col.strip().replace(' ', '_') for col in df.columns]

print(f"Columns after cleaning: {df.columns.tolist()}")

print("Connecting to SQLite database...")
conn = sqlite3.connect(db_path)

print("Writing data to table 'locations'...")
df.to_sql('locations', conn, if_exists='replace', index=False)

conn.close()
print("Done! CSV imported into SQLite database successfully.")
