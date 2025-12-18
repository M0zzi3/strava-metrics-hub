from . import db


class Athlete(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    strava_id = db.Column(db.Integer, unique=True, nullable=False)
    username = db.Column(db.String(80), nullable=True)

    # Auth tokens (We need these to fetch data in the background)
    access_token = db.Column(db.String(255), nullable=False)
    refresh_token = db.Column(db.String(255), nullable=False)
    expires_at = db.Column(db.Integer, nullable=False)  # Unix timestamp

    def __repr__(self):
        return f'<Athlete {self.username}>'


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    strava_id = db.Column(db.BigInteger, unique=True, nullable=False)  # Strava IDs are long
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50))  # Run, Ride, Swim

    # Metrics
    distance = db.Column(db.Float)  # usually in meters
    moving_time = db.Column(db.Integer)  # seconds
    total_elevation_gain = db.Column(db.Float)  # meters
    start_date = db.Column(db.DateTime, nullable=False)

    # For visualization
    summary_polyline = db.Column(db.Text, nullable=True)  # Map string

    def __repr__(self):
        return f'<Activity {self.name}>'