"""
Flask application factory for ACEest Fitness & Gym.
"""
import os
from flask import Flask
from app import models

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    # Configuration defaults
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "aceest-secret-dev-key-999"),
        DATABASE=os.environ.get("ACEEST_DB_PATH", "aceest_fitness.db")
    )

    if test_config:
        app.config.update(test_config)

    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize Database Schema
    db_path = app.config.get("DATABASE")
    models.init_db(db_path)

    # Seed baseline clients if database is fresh
    _seed_initial_data(db_path)

    # Register blueprints
    from app.routes import bp
    app.register_blueprint(bp)

    return app

def _seed_initial_data(db_path):
    existing = models.get_all_clients(db_path)
    if not existing:
        seeds = [
            {
                "name": "Karthik Subramanian",
                "age": 28,
                "height": 178.0,
                "weight": 82.5,
                "program": "Fat Loss (FL)",
                "calories": 1815,
                "target_weight": 75.0,
                "target_adherence": 85,
                "membership_status": "Active",
                "membership_expiry": "2026-12-31",
                "notes": "Focused on cutting body fat; tracking assaulted bike and 5x5 squats."
            },
            {
                "name": "Priya Natarajan",
                "age": 24,
                "height": 165.0,
                "weight": 58.0,
                "program": "Muscle Gain (MG)",
                "calories": 2030,
                "target_weight": 62.0,
                "target_adherence": 90,
                "membership_status": "Active",
                "membership_expiry": "2027-03-15",
                "notes": "Hypertrophy focus; PPL split; 120g daily protein target."
            },
            {
                "name": "Ramesh Kumar",
                "age": 35,
                "height": 172.0,
                "weight": 76.0,
                "program": "Beginner (BG)",
                "calories": 1976,
                "target_weight": 70.0,
                "target_adherence": 75,
                "membership_status": "Active",
                "membership_expiry": "2026-10-01",
                "notes": "Building routine consistency and movement technique form."
            }
        ]
        for s in seeds:
            models.save_client(s, db_path)
            # Add initial progress logs
            models.log_progress(s["name"], 80, "Week 42 - 2026", db_path)
            models.log_progress(s["name"], 85, "Week 43 - 2026", db_path)
            models.log_progress(s["name"], 90, "Week 44 - 2026", db_path)
