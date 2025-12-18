# Strava Metrics Hub

A self-hosted analytics dashboard for endurance athletes. This application synchronizes your Strava history into a local PostgreSQL database and provides interactive visualizations for training analysis.

Designed to give athletes ownership of their data with powerful tools for trend analysis and geospatial visualization.

## Architecture

The project follows a microservices-lite architecture using Docker:

*   **Web Container:** Python 3.9 + Flask application serving the UI and handling API logic.
*   **Database Container:** PostgreSQL 15 for persistent storage of activity data.
*   **Data Science Stack:** Pandas and NumPy for data transformation; Plotly and Folium for visualization.

## Key Features

*   **Smart Sync:** Incrementally fetches new activities from Strava using OAuth2.
*   **Performance Dashboard:**
    *   **Volume Analysis:** Weekly distance tracking.
    *   **Intensity Correlation:** Interactive chart comparing Speed vs. Heart Rate over time.
    *   **Cumulative Gains:** Elevation gain tracking.
*   **Geospatial Heatmap:** Aggregated map of all activity routes.
*   **Activity Archive:** Searchable, sortable log of all historical data.

## Getting Started

### Prerequisites

*   Docker Desktop (or Docker Engine + Compose)
*   A Strava Account

> **IMPORTANT FOR GRADING**
> For demonstration purposes, I have included a pre-filled `.env.example` file with my working API keys.
>
> **Action Required:** Rename `.env.example` to `.env` before running the project. Skip setup to the step 3. Launch
>
> If for some reason API won't work I have also included Screenshots of working web UI. 

### 1. Configure Strava API

1.  Go to your [Strava API Settings](https://www.strava.com/settings/api).
2.  Create an application to get your `Client ID`, `Client Secret` and `Refresh Token`.

### 2. Environment Setup

Create a `.env` file in the project root with your credentials:

```bash
# Database Configuration
POSTGRES_USER=strava_user
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=strava_db

# Strava API Credentials
STRAVA_CLIENT_ID=your_client_id
STRAVA_CLIENT_SECRET=your_client_secret
STRAVA_REFRESH_TOKEN=your_refresh_token
```

### 3. Launch

Start the application stack:

```bash
docker compose up -d --build
```

The application will be available at: **http://localhost:5000**

## Usage Guide

1.  **Initial Sync:** On the dashboard, click the "Sync Recent" button. For a complete history import, use the "Full Import" option (this may take time depending on your history size).
2.  **Analyze:** Browse the dashboard for high-level trends or the Activity Log for specific session details.
3.  **Map:** View the Heatmap tab to see your global activity footprint.

## Tech Stack

*   **Backend:** Flask, SQLAlchemy
*   **Database:** PostgreSQL
*   **Frontend:** Bootstrap 5, Jinja2
*   **Visualization:** Plotly.js, Folium
*   **Infrastructure:** Docker Compose

---
