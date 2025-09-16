# ASPR-Treatment-Locations

# ASPR Vaccine Locator & Healthcare Chatbot

A Flask-based web application that allows users to locate treatment providers, explore vaccination and medication availability, and interact with a healthcare chatbot powered by OpenAI. This project includes:

- **Provider view** – Search by state, city, or ZIP code; view KPIs and medication availability.
- **Customer view** – Interactive map to select states and view providers.
- **Chatbot** – Ask natural language questions about treatment locations, medications, and availability.
- **OpenAI integration** – Converts user queries into SQL queries safely.

---

## Table of Contents

- [Demo](#demo)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Environment Variables](#environment-variables)
- [Deployment](#deployment)
- [Folder Structure](#folder-structure)
- [Contributing](#contributing)
- [License](#license)

---

## Demo

*(You can include a screenshot or GIF here showing the map, chatbot, and provider view)*

---

## Features

1. **Provider Dashboard**
   - Search providers by state, city, or ZIP.
   - View KPIs such as number of providers, available medications, PAP sites, etc.
   - Chart visualization for state-level data.

2. **Customer Interactive Map**
   - Select states from a Google Maps interface.
   - Click on a state to view available providers.

3. **Healthcare Chatbot**
   - Ask natural language questions.
   - Returns provider locations, available medications (Paxlovid, Lagevrio, Veklury), and contact information.
   - Uses OpenAI GPT model to convert natural language queries into SQL.

4. **Secure API Key Management**
   - OpenAI API key is stored in environment variables, never hard-coded.

---

## Tech Stack

- **Frontend:** HTML, CSS (Bootstrap 5), JavaScript
- **Backend:** Python, Flask
- **Database:** SQLite (`aspr_data.db`)
- **AI:** OpenAI GPT-4
- **Hosting:** GitHub + Render (or any free Flask hosting platform)
- **Maps:** Google Maps JavaScript API

---

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/aspr-vaccine-locator.git
cd aspr-vaccine-locator
