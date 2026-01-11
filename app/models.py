from . import db


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    strava_id = db.Column(db.BigInteger, unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50))

    # Metrics
    distance = db.Column(db.Float)
    moving_time = db.Column(db.Integer)
    total_elevation_gain = db.Column(db.Float)
    start_date = db.Column(db.DateTime, nullable=False)
    summary_polyline = db.Column(db.Text, nullable=True)
    average_heartrate = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f'<Activity {self.name}>'
