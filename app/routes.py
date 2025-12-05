from flask import Blueprint

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return "<h1>It Works!</h1><p>Connected to DB successfully.</p>"