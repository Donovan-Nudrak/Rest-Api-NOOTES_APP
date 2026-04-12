#!/usr/bin/env python3
"""Flask application entrypoint: wires config, DB, and API blueprints."""

from flask import Flask
from config import DevelopmentConfig
from database.db import db

from routes.auth_routes import auth_bp
from routes.note_routes import note_bp

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

db.init_app(app)


app.register_blueprint(auth_bp)
app.register_blueprint(note_bp)


@app.route("/")
def index():
    return {"message": "API running"}, 200


# Ensure SQLite tables exist before handling requests (dev-friendly; use migrations in production).
with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)

