# Project Report: Strava Metrics Hub

**Student:** Maksymilian Piast  
**Project Title:** Strava Metrics Hub  
**Course:** Python Programming

---

## 1. Project Description

Strava Metrics Hub is a self-hosted analytics dashboard designed for endurance athletes. It solves the problem of ephemeral data access on cloud platforms by synchronizing Strava activity data into a local, persistent database. The application leverages Python’s data science stack to provide deep analytics, trend visualization, and statistics that go beyond the standard free tier of Strava.

**Core Philosophy:** "Own your data, visualize your progress."

The application is built as a containerized web service, making it portable and easy to deploy on any system with Docker.

---

## 2. Architecture & Design

The project uses a **Microservices-Lite** architecture orchestrated by Docker Compose.

### High-Level Components

1.  **Web Container (The Brain):**
    *   **Technology:** Python 3.9, Flask.
    *   **Role:** Runs the application logic, serves the web interface, and communicates with the Strava API.
    *   **Key Libraries:** `Flask` (Web Framework), `SQLAlchemy` (ORM), `Pandas` (Data Processing), `Plotly` (Visualization).

2.  **Database Container (The Memory):**
    *   **Technology:** PostgreSQL 15.
    *   **Role:** Persistently stores activity data.
    *   **Connection:** Accessed by the Web Container via a secure internal network.

### Data Flow

1.  **Sync:** The user triggers a sync. The Web Container authenticates with Strava via OAuth2, fetches JSON data, parses it, and saves it to PostgreSQL.
2.  **Analyze:** When the user views the dashboard, the app queries PostgreSQL using SQLAlchemy.
3.  **Visualize:** Pandas transforms the raw SQL data into DataFrames. Plotly generates interactive HTML charts from these frames, which are then rendered in the browser.

### Directory Structure

```text
/
├── app/
│   ├── __init__.py      # App Factory: Initializes Flask and Database
│   ├── models.py        # Data Models: Defines the 'Activity' database schema
│   ├── routes.py        # Controller: Handles URL requests and business logic
│   ├── strava_client.py # API Client: Handles OAuth2 and Strava API requests
│   └── templates/       # Views: HTML/Jinja2 templates for the UI
├── docker-compose.yml   # Infrastructure: Defines the multi-container setup
├── Dockerfile           # Build Instructions: Recipe for the Python environment
└── run.py               # Entry Point: Script to launch the server
```

---

## 3. Borrowed Code Statement

This project was developed with the assistance of an AI coding companion for architectural structuring, debugging, and generating boilerplate code (e.g., HTML templates, Flask setup). The core logic, design decisions, and implementation of specific features (like the sync engine logic and data visualization choices) were verified and implemented by the student.

Standard documentation for Flask, Bootstrap 5, and Plotly was used as a reference. No complete applications or large logic blocks were copied from external repositories.

---

## 4. Requirements

The project dependencies are frozen in the `requirements.txt` file included in this archive.

**Key Libraries:**
*   `Flask==3.1.2`: Web Framework
*   `Flask-SQLAlchemy==3.1.1`: Database ORM
*   `pandas`: Data Analysis
*   `plotly`: Interactive Charts
*   `folium`: Map Visualization
*   `requests`: HTTP Client for API
