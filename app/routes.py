from flask import Blueprint, jsonify, render_template, redirect, url_for, request
from .models import db, Activity
from .strava_client import StravaClient
import os
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.io as pio
import folium
import polyline
from plotly.subplots import make_subplots
import plotly.graph_objects as go

main = Blueprint('main', __name__)


@main.route('/')
def dashboard():
    activities = Activity.query.order_by(Activity.start_date.desc()).all()

    if not activities:
        print("Database empty. Triggering initial full sync...")
        return redirect(url_for('main.sync_data', mode='full'))

    # 1. Prepare Data
    data = []
    for a in activities:
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
    # We sort by date for correct plotting
    df_sorted = df.sort_values('date')

    df_run = df_sorted[df_sorted['type'] == 'Run']
    weekly_vol = df_run.resample('W', on='date')['distance_km'].sum().reset_index()

    fig_vol = px.bar(weekly_vol, x='date', y='distance_km',
                     title='Weekly Running Volume',
                     labels={'distance_km': 'Distance (km)', 'date': 'Week'})
    fig_vol.update_layout(height=350)  # Set fixed height
    chart_html = pio.to_html(fig_vol, full_html=False)

    # 4. NEW Chart 2: Speed vs Heart Rate Over Time (Dual Axis)
    # We focus on Runs to keep the scale consistent
    df_perf = df_run.dropna(subset=['heart_rate'])

    if not df_perf.empty:
        # Create figure with secondary y-axis
        fig_hr = make_subplots(specs=[[{"secondary_y": True}]])

        # Add Speed Line (Left Axis)
        fig_hr.add_trace(
            go.Scatter(x=df_perf['date'], y=df_perf['speed_kmh'], name="Speed (km/h)",
                       mode='lines+markers', line=dict(color='#1f77b4')),
            secondary_y=False,
        )

        # Add Heart Rate Line (Right Axis)
        fig_hr.add_trace(
            go.Scatter(x=df_perf['date'], y=df_perf['heart_rate'], name="Heart Rate (bpm)",
                       mode='lines+markers', line=dict(color='#d62728')),
            secondary_y=True,
        )

        # Layout details
        fig_hr.update_layout(
            title_text="Fitness Trend: Speed vs Heart Rate (Runs Only)",
            height=400,
            hovermode="x unified"  # Shows both values when you hover over a date
        )

        # Set axis titles
        fig_hr.update_yaxes(title_text="Speed (km/h)", secondary_y=False)
        fig_hr.update_yaxes(title_text="Heart Rate (bpm)", secondary_y=True)

        hr_chart_html = pio.to_html(fig_hr, full_html=False)
    else:
        hr_chart_html = "<div class='text-center p-5'>No Heart Rate Data Available</div>"

    # 5. Chart 3: Activity Breakdown (Pie Chart)
    # Counts how many runs vs rides
    fig_pie = px.pie(df, names='type', title='Activity Distribution', hole=0.4)
    fig_pie.update_layout(height=350)
    pie_chart_html = pio.to_html(fig_pie, full_html=False)

    # 6. Chart 4: Cumulative Elevation (Area Chart)
    # Sort by date first
    df_sorted = df.sort_values('date')
    # Calculate cumulative sum of elevation
    df_sorted['cum_elevation'] = df_sorted['elevation'].cumsum()

    fig_elev = px.area(df_sorted, x='date', y='cum_elevation',
                       title='Cumulative Elevation Gain (m)',
                       labels={'cum_elevation': 'Total Climbed (m)'})
    fig_elev.update_layout(height=350)
    elev_chart_html = pio.to_html(fig_elev, full_html=False)

    return render_template('dashboard.html',
                           total_km=total_km,
                           total_elevation=total_elevation,
                           count=activity_count,
                           chart_html=chart_html,  # Volume Bar
                           hr_chart_html=hr_chart_html,  # Speed vs HR
                           pie_chart_html=pie_chart_html,  # NEW Pie
                           elev_chart_html=elev_chart_html  # NEW Area
                           )


@main.route('/sync')
def sync_data():
    client = StravaClient()
    refresh_token = os.environ.get('STRAVA_REFRESH_TOKEN')

    # 1. Refresh Token
    token_data = client.refresh_access_token(refresh_token)
    if 'access_token' not in token_data:
        return f"Error: {token_data}", 400
    access_token = token_data['access_token']

    # 2. Determine Sync Mode
    # If mode='full', we ignore existing items and fetch EVERYTHING.
    mode = request.args.get('mode', 'recent')
    force_full = (mode == 'full')

    page = 1
    added_count = 0
    updated_count = 0
    keep_fetching = True

    print(f"--- Starting Sync (Mode: {mode}) ---")

    while keep_fetching:
        print(f"Fetching page {page}...")
        try:
            activities_json = client.get_activities(access_token, page=page)
        except Exception as e:
            print(f"API Error on page {page}: {e}")
            break

        # Strava returns an empty list [] when no more data
        if not activities_json or isinstance(activities_json, dict):
            break

        for act in activities_json:
            existing = Activity.query.filter_by(strava_id=act['id']).first()

            if existing:
                if not force_full:
                    # SMART STOP: We found an activity we already have.
                    # Assuming Strava sends newest first, we are now caught up.
                    print("Found existing activity. Stopping sync.")
                    keep_fetching = False
                    break
                else:
                    # In full mode, we might update existing records or just skip
                    # Let's skip to save time, but continue the loop
                    continue

            # If not existing, add it
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

        # Commit every page to be safe
        db.session.commit()

        # Safety break for school project (prevent infinite loops if logic fails)
        # 20 pages * 50 items = 1000 activities. Increase if you have more.
        if page > 20:
            break

        page += 1

    print(f"--- Sync Complete. Added {added_count} activities. ---")

    # 3. User Experience: Redirect back to Dashboard
    return redirect(url_for('main.dashboard'))