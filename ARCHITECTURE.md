# Architecture & Developer Guide

This document provides a deep dive into the **Strava Metrics Hub** codebase. It is designed to help you understand not just *what* the code does, but *why* it is structured this way and how data flows through the system.

## 1. System Overview (The "Big Picture")

The application follows a **Microservices-Lite** pattern using Docker. Instead of one giant program running on your computer, we run two isolated "mini-computers" (containers) that talk to each other.

### The Container Duo
1.  **`web` (Flask App):** This is the brain. It runs your Python code, serves the HTML pages to your browser, and talks to the Strava API.
2.  **`db` (PostgreSQL):** This is the memory. It stores your activity data safely on disk so it persists even if you restart the application.

**Communication Flow:**
*   **Browser -> Web Container:** Your browser sends a request (e.g., "Show me the dashboard") to `localhost:5000`.
*   **Web Container -> Database:** The Flask app asks the Database, "Give me all activities sorted by date."
*   **Web Container -> Strava API:** When syncing, the Flask app asks Strava, "Do you have any new runs?"

---

## 2. Directory Structure Explained

```text
/
├── app/
│   ├── __init__.py      # The "Factory": Starts the Flask app and connects extensions.
│   ├── models.py        # The "Blueprint": Defines what our data looks like in the DB.
│   ├── routes.py        # The "Traffic Controller": Decides what to do when you visit a URL.
│   ├── strava_client.py # The "Translator": Handles talking to the external Strava API.
│   └── templates/       # The "Face": HTML files that show the data to the user.
├── docker-compose.yml   # The "Orchestrator": Defines how the two containers work together.
├── Dockerfile           # The "Recipe": Instructions for building the Web container image.
└── run.py               # The "Ignition Key": The tiny script that starts the engine.
```

---

## 3. Code Deep Dive

### A. `app/__init__.py`: The Application Factory
**Purpose:** To create and configure the Flask application instance.
**Why use a factory?** It allows us to create multiple instances of our app with different configurations (e.g., one for testing, one for production) without changing the code.

**Key Logic:**
*   `db.init_app(app)`: Connects the SQLAlchemy database tool to our app.
*   `with app.app_context():`: This is a crucial line. Flask needs to know "which app are we talking about?" before it can touch the database. Inside this block, we import our models and create tables (`db.create_all()`) so the database is ready the moment the app starts.

### B. `app/models.py`: The Data Schema
**Purpose:** Defines the `Activity` class, which maps Python objects to the PostgreSQL `activities` table.
**Key Concept (ORM):** We use an ORM (Object-Relational Mapper). This lets us write Python code like `Activity.query.all()` instead of raw SQL like `SELECT * FROM activities`.

*   `db.Column`: Defines a column in the table.
*   `db.Integer`, `db.Float`: Defines the data type.

### C. `app/routes.py`: The Logic Center
**Purpose:** Handles user requests (URLs). Each function decorated with `@main.route` corresponds to a page.

**Key Functions:**
1.  `dashboard()` (`/`):
    *   **Fetches Data:** Queries the database for all activities.
    *   **Transforms Data:** Loops through the activities to calculate derived metrics (like speed in km/h) and prepares a list for the charts.
    *   **Visualizes:** Uses Plotly (`px.bar`, `make_subplots`) to generate interactive charts as HTML strings.
    *   **Renders:** Passes these HTML strings to the `dashboard.html` template.

2.  `sync_data()` (`/sync`):
    *   **Authenticates:** Uses `StravaClient` to get a fresh access token.
    *   **Loops:** Fetches pages of activities from Strava until it finds one we already have (Incremental Sync).
    *   **Saves:** Creates new `Activity` objects and adds them to the database session.
    *   **Commits:** `db.session.commit()` saves the batch to the database.

### D. `app/strava_client.py`: The API Handler
**Purpose:** Encapsulates all the complexity of talking to Strava.
**Why separate this?** If Strava changes their API URL tomorrow, we only have to update this one file, not every route that uses it.

**Key Logic:**
*   `refresh_access_token`: The most critical function. Strava access tokens expire after 6 hours. This function uses your permanent `refresh_token` to get a temporary `access_token` so the sync never breaks.

---

## 4. The Data Flow: "Syncing"

When you click **"Sync Recent"**, here is the exact chain of events:

1.  **User Click:** Browser sends `GET /sync` request.
2.  **Route Handler:** `routes.py` -> `sync_data()` function starts.
3.  **Auth:** `StravaClient` exchanges your Refresh Token for an Access Token.
4.  **Fetch:** `StravaClient` requests page 1 of your activities from Strava.
5.  **Check:** The code loops through the downloaded list.
    *   *If `strava_id` exists in DB:* Stop! We are up to date.
    *   *If `strava_id` is new:* Create an `Activity` object.
6.  **Save:** The new objects are staged (`db.session.add`).
7.  **Commit:** The transaction is committed to Postgres (`db.session.commit`).
8.  **Redirect:** The user is sent back to the dashboard to see the new data.

---

## 5. Developer Cheatsheet

**Database Migrations:**
Since we use `db.create_all()`, if you change `models.py` (e.g., add a column), the easiest way to update the DB in development is to delete the volume:
```bash
docker compose down -v
docker compose up -d
```
*(Warning: This deletes all data!)*

**Adding a New Chart:**
1.  Go to `routes.py` -> `dashboard()`.
2.  Create a Plotly figure (`fig = px.bar(...)`).
3.  Convert to HTML: `chart_html = pio.to_html(fig, full_html=False)`.
4.  Pass `chart_html` to `render_template`.
5.  Edit `dashboard.html` and add `{{ chart_html | safe }}` where you want it.
