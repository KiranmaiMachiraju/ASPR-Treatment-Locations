import requests
import pandas as pd
import sqlite3
import time

API_URL = 'https://healthdata.gov/resource/879u-23sm.json'
DB_PATH = 'aspr_data.db'
TABLE_NAME = 'locations'
CHUNK_SIZE = 1000  # Max allowed by API
OFFSET = 0

all_data = []

print("Fetching data from API...")

while True:
    params = {
        '$limit': CHUNK_SIZE,
        '$offset': OFFSET
    }

    print(f"Fetching rows {OFFSET} to {OFFSET + CHUNK_SIZE}...")
    response = requests.get(API_URL, params=params)

    if response.status_code != 200:
        print(f"Error fetching data: {response.status_code}")
        break

    chunk = response.json()
    if not chunk:
        print("No more data.")
        break

    all_data.extend(chunk)
    OFFSET += CHUNK_SIZE
    time.sleep(0.2)  # Be gentle to the server

# Convert to DataFrame
df = pd.DataFrame(all_data)

print(f"Total rows fetched: {len(df)}")

# Clean column names
df.columns = [col.strip().replace(' ', '_') for col in df.columns]

# Store in SQLite
print("Writing to database...")
conn = sqlite3.connect(DB_PATH)
df.to_sql(TABLE_NAME, conn, if_exists='replace', index=False)
conn.close()

print("Done!")
