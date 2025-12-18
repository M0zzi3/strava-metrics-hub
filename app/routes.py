from flask import Blueprint, jsonify
from .models import db, Activity
from .strava_client import StravaClient
import os
from datetime import datetime

main = Blueprint('main', __name__)


@main.route('/')
def index():
    # Simple count query
    count = Activity.query.count()
    return f"<h1>Strava Hub</h1><p>Activities in DB: {count}</p>"


@main.route('/sync')
def sync_data():
    client = StravaClient()

    refresh_token = os.environ.get('STRAVA_REFRESH_TOKEN')

    # 1. Check if token refresh worked
    token_data = client.refresh_access_token(refresh_token)
    if 'access_token' not in token_data:
        # Print the error to the docker logs and return it
        print(f"Token Error: {token_data}", flush=True)
        return jsonify({"error": "Failed to refresh token", "details": token_data}), 400

    access_token = token_data['access_token']

    # 2. Fetch Activities
    activities_json = client.get_activities(access_token, page=1)

    # --- SAFETY CHECK START ---
    # If Strava returns a dictionary (error), stop immediately.
    if isinstance(activities_json, dict):
        print(f"Strava API Error: {activities_json}", flush=True)
        return jsonify({"error": "Strava API returned an error", "strava_response": activities_json}), 400


    # 3. Save to DB
    added_count = 0
    for act in activities_json:
        # Check if exists
        existing = Activity.query.filter_by(strava_id=act['id']).first()
        if not existing:
            new_activity = Activity(
                strava_id=act['id'],
                name=act['name'],
                type=act['type'],
                distance=act['distance'],
                moving_time=act['moving_time'],
                total_elevation_gain=act.get('total_elevation_gain', 0),
                start_date=datetime.strptime(act['start_date'], "%Y-%m-%dT%H:%M:%SZ"),
                summary_polyline=act.get('map', {}).get('summary_polyline')
            )
            db.session.add(new_activity)
            added_count += 1
            pass

    db.session.commit()

    return jsonify({"status": "success", "added": added_count})