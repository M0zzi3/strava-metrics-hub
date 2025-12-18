from flask import Blueprint, jsonify, render_template
from .models import db, Activity
from .strava_client import StravaClient
import os
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.io as pio
import folium
import polyline

main = Blueprint('main', __name__)


@main.route('/')
def dashboard():
    activities = Activity.query.order_by(Activity.start_date.desc()).all()

    if not activities:
        return "<h1>No Data</h1><p>Go to <a href='/sync'>/sync</a> to import activities.</p>"

    # 1. Prepare Data
    data = []
    for a in activities:
        # Calculate Speed (m/s to km/h)
        speed_kmh = 0
        if a.moving_time > 0:
            speed_kmh = (a.distance / 1000) / (a.moving_time / 3600)

        data.append({
            'date': a.start_date,
            'type': a.type,
            'distance_km': a.distance / 1000,
            'elevation': a.total_elevation_gain,
            'heart_rate': a.average_heartrate,
            'speed_kmh': round(speed_kmh, 1)
        })

    df = pd.DataFrame(data)

    # 2. Key Metrics
    total_km = round(df['distance_km'].sum(), 2)
    total_elevation = int(df['elevation'].sum())
    activity_count = len(df)

    # 3. Chart 1: Weekly Volume (Bar Chart)
    df.set_index('date', inplace=True)
    weekly_vol = df[df['type'] == 'Run'].resample('W')['distance_km'].sum().reset_index()

    fig_vol = px.bar(weekly_vol, x='date', y='distance_km',
                     title='Weekly Running Volume',
                     labels={'distance_km': 'Distance (km)', 'date': 'Week'})
    chart_html = pio.to_html(fig_vol, full_html=False)

    # 4. Chart 2: Correlation Speed vs Heart Rate (Scatter Plot)
    # Filter out activities with no heart rate
    df_hr = df.dropna(subset=['heart_rate'])

    if not df_hr.empty:
        # This creates the correlation chart you asked for
        fig_hr = px.scatter(df_hr, x='speed_kmh', y='heart_rate', color='type',
                            title='Performance: Speed vs Heart Rate Correlation',
                            labels={'speed_kmh': 'Speed (km/h)', 'heart_rate': 'Avg HR (bpm)'},
                            hover_data=['distance_km'])
        hr_chart_html = pio.to_html(fig_hr, full_html=False)
    else:
        hr_chart_html = "<div class='text-center p-5'>No Heart Rate Data Available</div>"

    return render_template('dashboard.html',
                           total_km=total_km,
                           total_elevation=total_elevation,
                           count=activity_count,
                           chart_html=chart_html,
                           hr_chart_html=hr_chart_html)


@main.route('/sync')
def sync_data():
    client = StravaClient()
    refresh_token = os.environ.get('STRAVA_REFRESH_TOKEN')

    token_data = client.refresh_access_token(refresh_token)
    if 'access_token' not in token_data:
        return jsonify({"error": "Failed to refresh token", "details": token_data}), 400

    access_token = token_data['access_token']
    activities_json = client.get_activities(access_token, page=1)

    if isinstance(activities_json, dict):
        return jsonify({"error": "Strava API returned an error", "strava_response": activities_json}), 400

    added_count = 0
    for act in activities_json:
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
                summary_polyline=act.get('map', {}).get('summary_polyline'),
                average_heartrate=act.get('average_heartrate')
            )
            db.session.add(new_activity)
            added_count += 1

    db.session.commit()
    return jsonify({"status": "success", "added": added_count})


@main.route('/activities')
def activity_list():
    activities = Activity.query.order_by(Activity.start_date.desc()).all()
    return render_template('activities.html', activities=activities)


@main.route('/map')
def map_view():
    activities = Activity.query.filter(Activity.summary_polyline != None).all()
    start_coords = [51.2194, 4.4025]

    if activities:
        try:
            first_poly = polyline.decode(activities[0].summary_polyline)
            if first_poly:
                start_coords = first_poly[0]
        except:
            pass

    m = folium.Map(location=start_coords, zoom_start=13, tiles='CartoDB dark_matter')

    for act in activities:
        if act.summary_polyline:
            try:
                coords = polyline.decode(act.summary_polyline)
                color = '#ff4b4b' if act.type == 'Run' else '#0000ff'
                folium.PolyLine(coords, color=color, weight=2.5, opacity=0.6,
                                tooltip=f"{act.name}").add_to(m)
            except:
                continue

    map_html = m._repr_html_()
    return render_template('map.html', map_html=map_html)