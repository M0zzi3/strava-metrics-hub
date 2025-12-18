from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    # 1. Config
    app.config['SECRET_KEY'] = 'dev'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # 2. Register Blueprints
    from .routes import main
    app.register_blueprint(main)

    # 3. Create Tables (The Fix is here)
    with app.app_context():
        # IMPORT MODELS HERE so SQLAlchemy 'sees' them before creating tables
        from . import models

        db.create_all()

    return app