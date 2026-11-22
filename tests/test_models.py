"""
Unit tests for SQLite database operations and models in ACEest Fitness.
"""
from app import models

def test_client_crud(app):
    db_path = app.config["DATABASE"]
    # Create client
    client_data = {
        "name": "Anand Kumar",
        "age": 30,
        "height": 180.0,
        "weight": 85.0,
        "program": "Fat Loss (FL)",
        "calories": 1870,
        "target_weight": 78.0,
        "target_adherence": 80,
        "notes": "Testing CRUD operations"
    }
    saved = models.save_client(client_data, db_path)
    assert saved["name"] == "Anand Kumar"
    assert saved["weight"] == 85.0

    # Retrieve client
    fetched = models.get_client_by_name("Anand Kumar", db_path)
    assert fetched is not None
    assert fetched["program"] == "Fat Loss (FL)"

    # Update client
    client_data["weight"] = 83.5
    updated = models.save_client(client_data, db_path)
    assert updated["weight"] == 83.5

    # Delete client
    deleted = models.delete_client("Anand Kumar", db_path)
    assert deleted is True
    assert models.get_client_by_name("Anand Kumar", db_path) is None

def test_progress_logging(app):
    db_path = app.config["DATABASE"]
    models.save_client({"name": "Meena", "program": "Beginner (BG)"}, db_path)

    log_id = models.log_progress("Meena", 92, "Week 40 - 2026", db_path)
    assert log_id is not None

    records = models.get_progress_by_client("Meena", db_path)
    assert len(records) == 1
    assert records[0]["adherence"] == 92

def test_workout_and_exercise_logging(app):
    db_path = app.config["DATABASE"]
    models.save_client({"name": "Vijay", "program": "Muscle Gain (MG)"}, db_path)

    workout_data = {
        "client_name": "Vijay",
        "date": "2026-11-20",
        "workout_type": "Strength",
        "duration_min": 75,
        "notes": "PR on squats"
    }
    exercises = [
        {"name": "Back Squat", "sets": 5, "reps": 5, "weight": 110.0},
        {"name": "Leg Press", "sets": 4, "reps": 10, "weight": 160.0}
    ]
    w_id = models.log_workout(workout_data, exercises, db_path)
    assert w_id is not None

    workouts = models.get_workouts_by_client("Vijay", db_path)
    assert len(workouts) == 1
    assert workouts[0]["workout_type"] == "Strength"
    assert len(workouts[0]["exercises"]) == 2
    assert workouts[0]["exercises"][0]["name"] == "Back Squat"

def test_metric_logging(app):
    db_path = app.config["DATABASE"]
    models.save_client({"name": "Deepa", "program": "Fat Loss (FL)"}, db_path)

    m_data = {
        "client_name": "Deepa",
        "date": "2026-11-21",
        "weight": 64.5,
        "waist": 78.0,
        "bodyfat": 24.5
    }
    m_id = models.log_metric(m_data, db_path)
    assert m_id is not None

    metrics = models.get_metrics_by_client("Deepa", db_path)
    assert len(metrics) == 1
    assert metrics[0]["weight"] == 64.5
