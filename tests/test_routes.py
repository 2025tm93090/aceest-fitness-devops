"""
Integration tests for Flask HTTP routes and REST APIs in ACEest Fitness.
"""
import json

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["database"] == "healthy"
    assert "version" in data
    assert "uptime_seconds" in data

def test_version_endpoint(client):
    response = client.get("/version")
    assert response.status_code == 200
    data = response.get_json()
    assert "version" in data
    assert data["app"] == "ACEest Fitness & Gym Management"

def test_strategy_endpoint(client):
    response = client.get("/strategy")
    assert response.status_code == 200
    data = response.get_json()
    assert "strategy" in data
    assert "features" in data

def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"ACEest FUNCTIONAL FITNESS" in response.data

def test_clients_page(client):
    response = client.get("/clients")
    assert response.status_code == 200
    assert b"Client Management" in response.data

def test_workouts_page(client):
    response = client.get("/workouts")
    assert response.status_code == 200
    assert b"Workout Sessions" in response.data

def test_analytics_page(client):
    response = client.get("/analytics")
    assert response.status_code == 200
    assert b"Weekly Adherence Progress" in response.data

def test_deployments_page(client):
    response = client.get("/deployments")
    assert response.status_code == 200
    assert b"Kubernetes Progressive Deployment Engine" in response.data

def test_api_clients_crud(client):
    # Get all clients
    res = client.get("/api/clients")
    assert res.status_code == 200
    data = res.get_json()
    assert "clients" in data

    # Create new client
    new_client = {
        "name": "Siddharth Verma",
        "age": 27,
        "height": 176.0,
        "weight": 74.0,
        "program": "Beginner (BG)",
        "target_weight": 70.0
    }
    res_post = client.post(
        "/api/clients",
        data=json.dumps(new_client),
        content_type="application/json"
    )
    assert res_post.status_code == 200
    assert "saved successfully" in res_post.get_json()["message"]

    # Fetch specific client
    res_get = client.get("/api/clients/Siddharth%20Verma")
    assert res_get.status_code == 200
    assert res_get.get_json()["client"]["name"] == "Siddharth Verma"

    # Delete client
    res_del = client.delete("/api/clients/Siddharth%20Verma")
    assert res_del.status_code == 200

    # Verify not found after delete
    res_get_after = client.get("/api/clients/Siddharth%20Verma")
    assert res_get_after.status_code == 404

def test_api_calculate_calories(client):
    payload = {"weight": 80, "program": "Muscle Gain (MG)"}
    res = client.post("/api/calculate-calories", data=json.dumps(payload), content_type="application/json")
    assert res.status_code == 200
    data = res.get_json()
    assert data["calories"] == 2800  # 80 * 35

def test_api_calculate_calories_bad_request(client):
    payload = {"weight": -5}
    res = client.post("/api/calculate-calories", data=json.dumps(payload), content_type="application/json")
    assert res.status_code == 400

def test_api_calculate_bmi(client):
    payload = {"weight": 70, "height": 175}
    res = client.post("/api/calculate-bmi", data=json.dumps(payload), content_type="application/json")
    assert res.status_code == 200
    data = res.get_json()
    assert data["bmi"] == 22.9

def test_api_calculate_bmi_bad_request(client):
    payload = {"weight": 70}
    res = client.post("/api/calculate-bmi", data=json.dumps(payload), content_type="application/json")
    assert res.status_code == 400

def test_api_export_csv(client):
    res = client.get("/api/export/csv")
    assert res.status_code == 200
    assert res.mimetype == "text/csv"
    assert b"Name" in res.data


def test_api_workouts_flow(client):
    # Log workout
    workout_payload = {
        "client_name": "Karthik Subramanian",
        "date": "2026-11-22",
        "workout_type": "Conditioning",
        "duration_min": 45,
        "notes": "Assault bike intervals",
        "exercises": [{"name": "Assault Bike", "sets": 5, "reps": 10, "weight": 0}]
    }
    res_post = client.post("/api/workouts", data=json.dumps(workout_payload), content_type="application/json")
    assert res_post.status_code == 201
    assert "workout_id" in res_post.get_json()

    # Get workouts
    res_get = client.get("/api/workouts/Karthik%20Subramanian")
    assert res_get.status_code == 200
    workouts = res_get.get_json()["workouts"]
    assert len(workouts) >= 1

def test_api_metrics_flow(client):
    metric_payload = {
        "client_name": "Karthik Subramanian",
        "date": "2026-11-22",
        "weight": 81.0,
        "waist": 82.5,
        "bodyfat": 18.2
    }
    res_post = client.post("/api/metrics", data=json.dumps(metric_payload), content_type="application/json")
    assert res_post.status_code == 201

    res_get = client.get("/api/metrics/Karthik%20Subramanian")
    assert res_get.status_code == 200
    metrics = res_get.get_json()["metrics"]
    assert len(metrics) >= 1

def test_api_progress_flow(client):
    prog_payload = {
        "client_name": "Priya Natarajan",
        "adherence": 95,
        "week": "Week 46 - 2026"
    }
    res_post = client.post("/api/progress", data=json.dumps(prog_payload), content_type="application/json")
    assert res_post.status_code == 201

    res_get = client.get("/api/progress/Priya%20Natarajan")
    assert res_get.status_code == 200
    records = res_get.get_json()["progress"]
    assert len(records) >= 1

def test_api_generate_ai_program(client):
    payload = {"experience_level": "intermediate", "program_focus": "Muscle Gain (MG)"}
    res = client.post("/api/generate-program", data=json.dumps(payload), content_type="application/json")
    assert res.status_code == 200
    data = res.get_json()
    assert len(data["schedule"]) > 0

def test_api_export_pdf(client):
    res = client.get("/api/export/pdf/Karthik%20Subramanian")
    assert res.status_code == 200
    assert "attachment;filename=" in res.headers["Content-Disposition"]

def test_api_export_pdf_not_found(client):
    res = client.get("/api/export/pdf/NonExistentClient999")
    assert res.status_code == 404
