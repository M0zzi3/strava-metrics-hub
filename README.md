# 🏃 Strava Metrics Hub

A containerized Flask application for endurance athletes to sync, analyze, and visualize their Strava training history.

## 🌟 Features
* **OAuth2 Authentication:** Secure login via Strava API with automatic token refreshing.
* **Data Pipeline:** Fetches raw JSON data, parses it, and stores it in a PostgreSQL database.
* **Dashboard:** Interactive charts (Plotly) showing training volume trends.
* **Activity Log:** Searchable and sortable history table (DataTables.js).
* **Geospatial Heatmap:** Interactive map visualizing all run/ride routes (Folium).
* **Infrastructure:** Fully dockerized (Flask + PostgreSQL) for easy deployment.

## 🛠 Technology Stack
* **Backend:** Python 3.9, Flask, SQLAlchemy
* **Database:** PostgreSQL 15
* **Frontend:** Bootstrap 5, Jinja2, Plotly, Folium
* **DevOps:** Docker, Docker Compose
* **External API:** Strava V3 API

## 🚀 How to Run

### Prerequisites
* Docker & Docker Compose installed
* A Strava Account & API Application (Client ID/Secret)

### 1. Setup Environment
Create a `.env` file in the root directory:
```bash
POSTGRES_USER=strava_user
POSTGRES_PASSWORD=password
POSTGRES_DB=strava_db

STRAVA_CLIENT_ID=your_id
STRAVA_CLIENT_SECRET=your_secret
STRAVA_REFRESH_TOKEN=your_refresh_token