"""
Flask Web Routes and REST API Controllers for ACEest Fitness & Gym.
Includes DevOps health checks, version tracking, and deployment strategy endpoints.
"""
import os
import time
from datetime import datetime, date
from flask import Blueprint, render_template, request, jsonify, Response, current_app

from app import models, services

bp = Blueprint("main", __name__)
START_TIME = time.time()

# DevOps metadata from environment (configured via ConfigMap/Docker/Jenkins)
APP_VERSION = os.environ.get("APP_VERSION", "v3.0.0")
APP_ENVIRONMENT = os.environ.get("APP_ENVIRONMENT", "production")
DEPLOYMENT_STRATEGY = os.environ.get("DEPLOYMENT_STRATEGY", "RollingUpdate")
COLOR_VARIANT = os.environ.get("COLOR_VARIANT", "blue")  # blue or green for Blue-Green

# ----------------- DEVOPS & SYSTEM HEALTH ENDPOINTS -----------------

@bp.route("/health", methods=["GET"])
def health_check():
    """
    Kubernetes Liveness and Readiness Probe.
    Validates database connectivity and application health.
    """
    db_status = "healthy"
    try:
        conn = models.get_connection()
        conn.execute("SELECT 1")
        conn.close()
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
        return jsonify({
            "status": "unhealthy",
            "database": db_status,
            "version": APP_VERSION,
            "timestamp": datetime.utcnow().isoformat()
        }), 503

    uptime_sec = int(time.time() - START_TIME)
    return jsonify({
        "status": "healthy",
        "database": db_status,
        "version": APP_VERSION,
        "environment": APP_ENVIRONMENT,
        "strategy": DEPLOYMENT_STRATEGY,
        "color_variant": COLOR_VARIANT,
        "uptime_seconds": uptime_sec,
        "timestamp": datetime.utcnow().isoformat()
    }), 200

@bp.route("/version", methods=["GET"])
def get_version():
    """Returns application semantic version and deployment metadata."""
    return jsonify({
        "app": "ACEest Fitness & Gym Management",
        "version": APP_VERSION,
        "environment": APP_ENVIRONMENT,
        "deployment_strategy": DEPLOYMENT_STRATEGY,
        "color_variant": COLOR_VARIANT,
        "commit": os.environ.get("GIT_COMMIT", "dev-local")
    }), 200

@bp.route("/strategy", methods=["GET"])
def get_strategy():
    """Returns current active deployment strategy configuration."""
    return jsonify({
        "strategy": DEPLOYMENT_STRATEGY,
        "variant": COLOR_VARIANT,
        "version": APP_VERSION,
        "features": {
            "v1_core_programs": True,
            "v2_tracking_analytics": True,
            "v3_ai_planner_and_pdf": True
        }
    }), 200

# ----------------- WEB UI ROUTES -----------------

@bp.route("/", methods=["GET"])
def index():
    """Homepage: Workout programs, Tamil Nadu nutrition plan, and quick summary."""
    return render_template(
        "index.html",
        programs=services.PROGRAMS,
        version=APP_VERSION,
        strategy=DEPLOYMENT_STRATEGY,
        color_variant=COLOR_VARIANT
    )

@bp.route("/clients", methods=["GET"])
def clients_view():
    """Client Management Dashboard."""
    clients = models.get_all_clients()
    return render_template(
        "clients.html",
        clients=clients,
        programs=services.PROGRAMS,
        version=APP_VERSION
    )

@bp.route("/workouts", methods=["GET"])
def workouts_view():
    """Workouts and Exercises Management."""
    clients = models.get_all_clients()
    return render_template(
        "workouts.html",
        clients=clients,
        version=APP_VERSION
    )

@bp.route("/analytics", methods=["GET"])
def analytics_view():
    """Progress & Adherence Analytics."""
    clients = models.get_all_clients()
    return render_template(
        "analytics.html",
        clients=clients,
        version=APP_VERSION
    )

@bp.route("/deployments", methods=["GET"])
def deployments_view():
    """Live DevOps Deployment Strategies Demonstration Panel."""
    return render_template(
        "deployments.html",
        version=APP_VERSION,
        strategy=DEPLOYMENT_STRATEGY,
        color_variant=COLOR_VARIANT,
        env=APP_ENVIRONMENT
    )

# ----------------- REST API CONTROLLERS -----------------

@bp.route("/api/programs", methods=["GET"])
def api_programs():
    """Returns all available fitness and nutrition programs."""
    return jsonify(services.PROGRAMS), 200

@bp.route("/api/clients", methods=["GET"])
def api_get_clients():
    """Returns all registered clients."""
    clients = models.get_all_clients()
    return jsonify({"clients": clients, "count": len(clients)}), 200

@bp.route("/api/clients/<name>", methods=["GET"])
def api_get_client(name):
    """Returns a specific client with full profile and recent metrics."""
    client = models.get_client_by_name(name)
    if not client:
        return jsonify({"error": f"Client '{name}' not found"}), 404
    progress = models.get_progress_by_client(name)
    workouts = models.get_workouts_by_client(name)
    metrics = models.get_metrics_by_client(name)
    return jsonify({
        "client": client,
        "progress": progress,
        "workouts": workouts,
        "metrics": metrics
    }), 200

@bp.route("/api/clients", methods=["POST"])
def api_save_client():
    """Creates or updates a client profile."""
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "Field 'name' is required"}), 400

    program = data.get("program", "Beginner (BG)")
    weight = data.get("weight")
    if weight is not None:
        try:
            weight = float(weight)
            data["weight"] = weight
            # Automatically calculate calories if not explicitly given
            if not data.get("calories"):
                data["calories"] = services.calculate_calories(weight, program)
        except ValueError:
            return jsonify({"error": "Weight must be a valid number"}), 400

    saved = models.save_client(data)
    return jsonify({"message": f"Client '{name}' saved successfully", "client": saved}), 200

@bp.route("/api/clients/<name>", methods=["DELETE"])
def api_delete_client(name):
    """Deletes a client profile and associated records."""
    deleted = models.delete_client(name)
    if not deleted:
        return jsonify({"error": f"Client '{name}' not found"}), 404
    return jsonify({"message": f"Client '{name}' deleted successfully"}), 200

@bp.route("/api/calculate-calories", methods=["POST"])
def api_calc_calories():
    """Calculates target calories for a given weight and program."""
    data = request.get_json() or {}
    weight = data.get("weight")
    program = data.get("program", "Beginner (BG)")
    if weight is None or float(weight) <= 0:
        return jsonify({"error": "Valid positive weight is required"}), 400
    calories = services.calculate_calories(float(weight), program)
    return jsonify({"program": program, "weight": float(weight), "calories": calories}), 200

@bp.route("/api/calculate-bmi", methods=["POST"])
def api_calc_bmi():
    """Calculates BMI and returns classification and health recommendation."""
    data = request.get_json() or {}
    weight = data.get("weight")
    height = data.get("height")
    if not weight or not height:
        return jsonify({"error": "Both weight (kg) and height (cm) are required"}), 400
    try:
        res = services.calculate_bmi(float(weight), float(height))
        return jsonify(res), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@bp.route("/api/progress", methods=["POST"])
def api_log_progress():
    """Logs weekly adherence for a client."""
    data = request.get_json() or {}
    client_name = data.get("client_name")
    adherence = data.get("adherence")
    if not client_name or adherence is None:
        return jsonify({"error": "client_name and adherence are required"}), 400
    try:
        adherence_int = int(adherence)
        if adherence_int < 0 or adherence_int > 100:
            return jsonify({"error": "Adherence must be between 0 and 100"}), 400
    except ValueError:
        return jsonify({"error": "Adherence must be an integer"}), 400

    week = data.get("week")
    log_id = models.log_progress(client_name, adherence_int, week)
    return jsonify({"message": "Weekly progress logged", "id": log_id}), 201

@bp.route("/api/progress/<name>", methods=["GET"])
def api_get_progress(name):
    """Retrieves progress logs for a client."""
    records = models.get_progress_by_client(name)
    return jsonify({"client": name, "progress": records}), 200

@bp.route("/api/workouts", methods=["POST"])
def api_log_workout():
    """Logs a workout session with exercises."""
    data = request.get_json() or {}
    client_name = data.get("client_name")
    if not client_name:
        return jsonify({"error": "client_name is required"}), 400
    exercises = data.get("exercises", [])
    workout_id = models.log_workout(data, exercises)
    return jsonify({"message": "Workout logged", "workout_id": workout_id}), 201

@bp.route("/api/workouts/<name>", methods=["GET"])
def api_get_workouts(name):
    """Retrieves workouts logged for a client."""
    workouts = models.get_workouts_by_client(name)
    return jsonify({"client": name, "workouts": workouts}), 200

@bp.route("/api/metrics", methods=["POST"])
def api_log_metric():
    """Logs body metrics (weight, waist, bodyfat)."""
    data = request.get_json() or {}
    client_name = data.get("client_name")
    if not client_name:
        return jsonify({"error": "client_name is required"}), 400
    metric_id = models.log_metric(data)
    return jsonify({"message": "Metrics logged", "metric_id": metric_id}), 201

@bp.route("/api/metrics/<name>", methods=["GET"])
def api_get_metrics(name):
    """Retrieves metrics history for a client."""
    metrics = models.get_metrics_by_client(name)
    return jsonify({"client": name, "metrics": metrics}), 200

@bp.route("/api/generate-program", methods=["POST"])
def api_generate_program():
    """Generates an AI workout schedule."""
    data = request.get_json() or {}
    exp = data.get("experience_level", "intermediate")
    focus = data.get("program_focus", "Beginner (BG)")
    schedule = services.generate_ai_workout_program(exp, focus)
    return jsonify({"experience_level": exp, "focus": focus, "schedule": schedule}), 200

@bp.route("/api/export/csv", methods=["GET"])
def api_export_csv():
    """Exports client database as CSV download."""
    clients = models.get_all_clients()
    csv_data = services.generate_csv_report(clients)
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=aceest_clients.csv"}
    )

@bp.route("/api/export/pdf/<name>", methods=["GET"])
def api_export_pdf(name):
    """Generates and downloads PDF profile for a client."""
    client = models.get_client_by_name(name)
    if not client:
        return jsonify({"error": f"Client '{name}' not found"}), 404
    pdf_bytes = services.generate_pdf_report(client)
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": f"attachment;filename={name}_report.pdf"}
    )
