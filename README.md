# ASPR Vaccine Locator & Healthcare Chatbot

A Flask-based web application that allows users to locate treatment providers, explore vaccination and medication availability, and interact with a healthcare chatbot powered by OpenAI GPT-4.

---

## Table of Contents

- [Demo](#demo)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Database Schema](#database-schema)
- [API Endpoints](#api-endpoints)
- [Installation](#installation)
- [Usage](#usage)
- [Environment Variables](#environment-variables)
- [Deployment](#deployment)
- [Future Improvements](#future-improvements)
- [References](#references)

---

## Web Application

Deployed at: https://aspr-treatment-locations.onrender.com

Tableau Public Viz: [ASPR Locations Dashboard](https://public.tableau.com/app/profile/kiranmai.machiraju5332/viz/ASPRLocations/Dashboard2)

---

## Features

1. **Provider Dashboard**
   - Search providers by state, city, or ZIP.
   - View KPIs: total providers, medications available, PAP sites, etc.
   - Charts for state-level provider distribution and medication availability.

2. **Customer Interactive Map**
   - Google Maps interface to select states.
   - Clickable markers for providers.

3. **Healthcare Chatbot**
   - Ask natural language questions.
   - Returns provider locations, available medications (Paxlovid, Lagevrio, Veklury), and contact info.
   - Uses OpenAI GPT-4 to convert natural language queries into SQL queries safely.

4. **Secure API Key Management**
   - OpenAI API key stored in environment variables (`.env` file), not hard-coded.

5. **Responsive Design**
   - Bootstrap 5 for mobile-friendly layout.
   - Deep blue metallic theme across chatbot and cards.

---

## Tech Stack

- **Frontend:** HTML, CSS (Bootstrap 5), JavaScript  
- **Backend:** Python, Flask  
- **Database:** SQLite (`aspr_data.db`)  
- **AI:** OpenAI GPT-4  
- **Hosting:** GitHub + Render (or any free Flask hosting platform)  
- **Maps:** Google Maps JavaScript API  

---

## Database Schema

### Table: `locations`

| Column Name                   | Type    | Description |
|--------------------------------|--------|-------------|
| `Provider_Name`               | TEXT   | Provider name |
| `Address_1`                   | TEXT   | Address line 1 |
| `Address_2`                   | TEXT   | Address line 2 |
| `City`                        | TEXT   | City |
| `State`                       | TEXT   | State code (e.g., GA, GU) |
| `Zip`                         | TEXT   | ZIP code |
| `Public_Phone`                | TEXT   | Phone number |
| `Latitude`                    | REAL   | Latitude coordinate |
| `Longitude`                   | REAL   | Longitude coordinate |
| `Geopoint`                    | TEXT   | Optional geopoint data |
| `Last_Report_Date`            | TEXT   | Last report date |
| `Is_PAP_Site`                 | INTEGER | 1 if PAP site |
| `Prescribing_Services_Available` | INTEGER | 1 if prescribing services available |
| `Appointment_URL`             | TEXT   | Appointment booking URL |
| `Home_Delivery`               | INTEGER | 1 if home delivery available |
| `Is_ICATT_Site`               | INTEGER | 1 if ICATT site |
| `Has_USG_Product`             | INTEGER | 1 if USG product available |
| `Has_Commercial_Product`      | INTEGER | 1 if commercial product available |
| `Has_Paxlovid`                | INTEGER | 1 if Paxlovid available |
| `Has_Commercial_Paxlovid`     | INTEGER | 1 if commercial Paxlovid available |
| `Has_USG_Paxlovid`            | INTEGER | 1 if USG Paxlovid available |
| `Has_Lagevrio`                | INTEGER | 1 if Lagevrio available |
| `Has_Commercial_Lagevrio`     | INTEGER | 1 if commercial Lagevrio available |
| `Has_USG_Lagevrio`            | INTEGER | 1 if USG Lagevrio available |
| `Has_Veklury`                 | INTEGER | 1 if Veklury available |
| `Has_Oseltamivir_Generic`     | INTEGER | 1 if generic Oseltamivir available |
| `Has_Oseltamivir_Suspension`  | INTEGER | 1 if Oseltamivir suspension available |
| `Has_Oseltamivir_Tamiflu`     | INTEGER | 1 if Tamiflu available |
| `Has_Baloxavir`               | INTEGER | 1 if Baloxavir available |
| `Has_Zanamivir`               | INTEGER | 1 if Zanamivir available |
| `Has_Peramivir`               | INTEGER | 1 if Peramivir available |
| `Grantee_Code`                | TEXT    | Internal code for grantee |
| `Is_Flu`                      | INTEGER | 1 if flu treatment available |
| `Is_COVID-19`                 | INTEGER | 1 if COVID-19 treatment/vaccine available |

---

## API Endpoints

- **`/api/states`**  
  Returns JSON with all states and approximate coordinates for map markers.

- **`/api/chatbot`**  
  Accepts a query parameter `question` and returns a JSON response with answers.  
  Example: `/api/chatbot?question=Where can I get Paxlovid in GA?`

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/aspr-vaccine-locator.git
cd aspr-vaccine-locator

2. Create a virtual environment and install dependencies:

python3 -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

3. Create a .env file:

pip install -r requirements.txt

4. Run the app locally

python app.py

Visit http://127.0.0.1:5000/ in your browser.
