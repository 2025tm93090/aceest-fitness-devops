"""
Unit tests for domain logic and business services in ACEest Fitness.
"""
import pytest
from app import services

def test_calculate_calories_fat_loss():
    # Weight: 80kg, Fat Loss factor: 22 -> 1760 kcal
    cal = services.calculate_calories(80.0, "Fat Loss (FL)")
    assert cal == 1760

def test_calculate_calories_muscle_gain():
    # Weight: 70kg, Muscle Gain factor: 35 -> 2450 kcal
    cal = services.calculate_calories(70.0, "Muscle Gain (MG)")
    assert cal == 2450

def test_calculate_calories_beginner():
    # Weight: 75kg, Beginner factor: 26 -> 1950 kcal
    cal = services.calculate_calories(75.0, "Beginner (BG)")
    assert cal == 1950

def test_calculate_calories_invalid():
    assert services.calculate_calories(0, "Fat Loss (FL)") is None
    assert services.calculate_calories(-10, "Fat Loss (FL)") is None

def test_calculate_bmi_normal():
    # 70kg, 175cm -> BMI = 70 / (1.75^2) = 22.86 -> 22.9
    res = services.calculate_bmi(70.0, 175.0)
    assert res["bmi"] == 22.9
    assert res["category"] == "Normal Weight"
    assert "Optimal health profile" in res["health_risk"]

def test_calculate_bmi_overweight():
    # 85kg, 170cm -> BMI = 85 / (1.7^2) = 29.4
    res = services.calculate_bmi(85.0, 170.0)
    assert res["bmi"] == 29.4
    assert res["category"] == "Overweight"
    assert res["recommended_program"] == "Fat Loss (FL)"

def test_calculate_bmi_invalid():
    with pytest.raises(ValueError):
        services.calculate_bmi(-70.0, 170.0)
    with pytest.raises(ValueError):
        services.calculate_bmi(70.0, 0)

def test_ai_workout_generator_beginner():
    schedule = services.generate_ai_workout_program("beginner", "Beginner (BG)")
    # 3 days for beginner, 3 exercises per day -> 9 items
    assert len(schedule) == 9
    days = {s["day"] for s in schedule}
    assert len(days) == 3
    for s in schedule:
        assert 2 <= s["sets"] <= 3
        assert 8 <= s["reps"] <= 12

def test_ai_workout_generator_advanced():
    schedule = services.generate_ai_workout_program("advanced", "Muscle Gain (MG)")
    # 5 days for advanced, 5 exercises per day -> 25 items
    assert len(schedule) == 25
    days = {s["day"] for s in schedule}
    assert len(days) == 5

def test_generate_csv_report():
    clients = [
        {"id": 1, "name": "Test User", "age": 25, "height": 170, "weight": 70,
         "program": "Beginner (BG)", "calories": 1950, "target_weight": 68,
         "target_adherence": 85, "membership_status": "Active"}
    ]
    csv_str = services.generate_csv_report(clients)
    assert "Test User" in csv_str
    assert "Beginner (BG)" in csv_str
