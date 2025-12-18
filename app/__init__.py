from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    # Secure key
    app.config['SECRET_KEY'] = 'dev'

    # Database connection (reads from Docker env)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Register blueprints
    from .routes import main
    app.register_blueprint(main)

    from .models import Athlete, Activity

    # Create tables
    with app.app_context():
        db.create_all()

    return app