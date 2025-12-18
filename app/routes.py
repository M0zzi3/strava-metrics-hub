from flask import Blueprint, jsonify, render_template # Add render_template
from .models import db, Activity
from .strava_client import StravaClient
import os
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.io as pio

main = Blueprint('main', __name__)


@main.route('/')
def dashboard():
    # 1. Fetch data from DB
    activities = Activity.query.order_by(Activity.start_date.desc()).all()

    if not activities:
        return "<h1>No Data</h1><p>Go to <a href='/sync'>/sync</a> to import activities.</p>"

    # 2. Convert to Pandas DataFrame for easy math
    data = [{
        'date': a.start_date,
        'distance_km': a.distance / 1000,  # Convert m to km
        'type': a.type,
        'elevation': a.total_elevation_gain
    } for a in activities]

    df = pd.DataFrame(data)

    # 3. Calculate Key Metrics
    total_km = round(df['distance_km'].sum(), 2)
    total_elevation = int(df['elevation'].sum())
    activity_count = len(df)

    # 4. Generate Plotly Chart (Weekly Volume)
    # Resample by week ('W') and sum distance
    df.set_index('date', inplace=True)
    weekly_vol = df[df['type'] == 'Run'].resample('W')['distance_km'].sum().reset_index()

    fig = px.bar(weekly_vol, x='date', y='distance_km',
                 title='Weekly Running Volume (km)',
                 labels={'distance_km': 'Distance (km)', 'date': 'Week'})

    # Convert chart to HTML to embed
    chart_html = pio.to_html(fig, full_html=False)

    return render_template('dashboard.html',
                           total_km=total_km,
                           total_elevation=total_elevation,
                           count=activity_count,
                           chart_html=chart_html)


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