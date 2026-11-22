"""
Business logic and domain services for ACEest Fitness & Gym.
Contains program specifications, nutrition logic, BMI calculation,
AI workout program generation, and data export routines.
"""
import random
from typing import Dict, Any, List, Optional

# Core Fitness Program Specifications (from original ACEest Assignment 1)
PROGRAMS = {
    "Fat Loss (FL)": {
        "workout": (
            "Mon: 5x5 Back Squat + AMRAP Core\n"
            "Tue: EMOM 20min Assault Bike & Kettlebell Swings\n"
            "Wed: Bench Press + 21-15-9 Thrusters/Burpees\n"
            "Thu: 10RFT Deadlifts & Box Jumps\n"
            "Fri: 30min Active Recovery & Zone 2 Cardio"
        ),
        "diet": (
            "Breakfast: 3 Egg Whites + Oats Idli / Sambar\n"
            "Lunch: Grilled Chicken (200g) + Brown Rice + Greens\n"
            "Dinner: Fish Curry + Millet Roti (Tamil Nadu Context)\n"
            "Hydration: 3.5 Liters Water/day"
        ),
        "color": "#e74c3c",
        "calorie_factor": 22,
        "description": "High-intensity metabolic conditioning with caloric deficit."
    },
    "Muscle Gain (MG)": {
        "workout": (
            "Mon: Back Squat 5x5 + Leg Press 4x10\n"
            "Tue: Barbell Bench Press 5x5 + Incline DB Press 4x8\n"
            "Wed: Conventional Deadlift 4x6 + Pull-ups 4xMax\n"
            "Thu: Overhead Press 4x8 + Dumbbell Lateral Raises 4x12\n"
            "Fri: Barbell Bent-over Rows 4x10 + Bicep/Tricep Supersets\n"
            "Sat: Heavy Carry / Core & Sled Push"
        ),
        "diet": (
            "Breakfast: 4 Whole Eggs + Peanut Butter Oatmeal + Banana\n"
            "Lunch: Chicken Biryani (250g Chicken breast) + Curd\n"
            "Dinner: Mutton Curry / Paneer + Jeera Rice + Dal\n"
            "Protein Target: 2.0g per kg body weight"
        ),
        "color": "#2ecc71",
        "calorie_factor": 35,
        "description": "Hypertrophy and progressive overload strength split."
    },
    "Beginner (BG)": {
        "workout": (
            "Circuit Training (3 Days/Week):\n"
            "- Air Squats: 3 sets x 15 reps\n"
            "- Ring Rows / Inverted Rows: 3 sets x 10 reps\n"
            "- Push-ups / Knee Push-ups: 3 sets x 10 reps\n"
            "- Plank Hold: 3 sets x 30 seconds\n"
            "Focus: Movement technique, joint mobility, form mastery."
        ),
        "diet": (
            "Balanced South Indian Whole Food Meals:\n"
            "- Breakfast: Idli / Dosa with Chana Sambar & boiled eggs\n"
            "- Lunch: Brown Rice, Dal, Keerai (Spinach), Curd\n"
            "- Dinner: 3 Chapatis with Paneer or Soy Stir-Fry\n"
            "Protein Target: 100-120g/day"
        ),
        "color": "#3498db",
        "calorie_factor": 26,
        "description": "Foundational movement literacy and consistency building."
    }
}

EXERCISE_POOLS = {
    "Strength": [
        "Back Squat", "Conventional Deadlift", "Barbell Bench Press",
        "Overhead Barbell Press", "Weighted Pull-Up", "Barbell Row",
        "Front Squat", "Romanian Deadlift"
    ],
    "Hypertrophy": [
        "Leg Press", "Incline Dumbbell Press", "Lat Pulldown",
        "Dumbbell Lateral Raise", "Barbell Bicep Curl", "Tricep Rope Pushdown",
        "Seated Cable Row", "Hamstring Leg Curl"
    ],
    "Conditioning": [
        "Assault Bike Sprint", "Rowing Machine Intervals", "Burpee Box Jump",
        "Kettlebell Swings", "Double-Unders / Jump Rope", "Medicine Ball Slams",
        "Farmer's Walk", "Prowler Sled Push"
    ],
    "Full Body": [
        "Push-Up", "Pull-Up", "Walking Lunge", "Plank Hold",
        "Dumbbell Goblet Squat", "Renegade Row", "Russian Twist"
    ]
}

def calculate_calories(weight_kg: float, program_name: str) -> Optional[int]:
    """Calculates daily target calories based on weight and program factor."""
    if not weight_kg or weight_kg <= 0:
        return None
    prog = PROGRAMS.get(program_name)
    factor = prog["calorie_factor"] if prog else 25
    return int(round(weight_kg * factor))

def calculate_bmi(weight_kg: float, height_cm: float) -> Dict[str, Any]:
    """Calculates BMI and returns classification and health recommendations."""
    if not weight_kg or weight_kg <= 0 or not height_cm or height_cm <= 0:
        raise ValueError("Weight and height must be positive numbers.")

    height_m = height_cm / 100.0
    bmi = round(weight_kg / (height_m * height_m), 1)

    if bmi < 18.5:
        category = "Underweight"
        risk = "Potential nutrient deficiency and low energy. Caloric surplus recommended."
        recommended_program = "Muscle Gain (MG)"
    elif bmi < 24.9:
        category = "Normal Weight"
        risk = "Optimal health profile. Maintain activity with functional strength training."
        recommended_program = "Beginner (BG)"
    elif bmi < 29.9:
        category = "Overweight"
        risk = "Moderate health risk. Focus on caloric control and progressive conditioning."
        recommended_program = "Fat Loss (FL)"
    else:
        category = "Obese"
        risk = "Elevated health risk. Prioritize structured fat loss, nutrition, and supervised conditioning."
        recommended_program = "Fat Loss (FL)"

    return {
        "bmi": bmi,
        "category": category,
        "health_risk": risk,
        "recommended_program": recommended_program
    }

def generate_ai_workout_program(experience_level: str, program_focus: str) -> List[Dict[str, Any]]:
    """
    Generates a personalized weekly training schedule based on experience and target program.
    """
    exp = (experience_level or "beginner").strip().lower()
    focus = "Full Body"
    if "Fat Loss" in program_focus:
        focus = "Conditioning"
    elif "Muscle Gain" in program_focus:
        focus = "Hypertrophy"
    elif "Beginner" in program_focus:
        focus = "Full Body"

    if exp == "beginner":
        days_count = 3
        sets_range = (2, 3)
        reps_range = (8, 12)
        ex_per_day = 3
    elif exp == "intermediate":
        days_count = 4
        sets_range = (3, 4)
        reps_range = (8, 15)
        ex_per_day = 4
    else:  # advanced
        days_count = 5
        sets_range = (4, 5)
        reps_range = (6, 12)
        ex_per_day = 5

    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    selected_days = weekdays[:days_count]
    pool = EXERCISE_POOLS.get(focus, EXERCISE_POOLS["Full Body"])

    schedule = []
    for day in selected_days:
        # Sample exercises without replacement if pool is large enough
        count = min(ex_per_day, len(pool))
        chosen_exercises = random.sample(pool, count)
        for ex in chosen_exercises:
            schedule.append({
                "day": day,
                "exercise": ex,
                "sets": random.randint(*sets_range),
                "reps": random.randint(*reps_range),
                "focus": focus
            })

    return schedule

def generate_csv_report(clients: List[Dict[str, Any]]) -> str:
    """Generates CSV string content for client list."""
    import io
    import csv
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "Name", "Age", "Height (cm)", "Weight (kg)", "Program",
        "Daily Calories", "Target Weight", "Target Adherence %", "Membership Status"
    ])
    for c in clients:
        writer.writerow([
            c.get("id"), c.get("name"), c.get("age"), c.get("height"),
            c.get("weight"), c.get("program"), c.get("calories"),
            c.get("target_weight"), c.get("target_adherence"), c.get("membership_status")
        ])
    return output.getvalue()

def generate_pdf_report(client_data: Dict[str, Any]) -> bytes:
    """
    Generates a PDF report for a client using fpdf2 if available,
    otherwise returns a UTF-8 text-based summary document.
    """
    try:
        from fpdf import FPDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 18)
        pdf.cell(0, 12, "ACEest Fitness & Performance - Client Profile", ln=True, align="C")
        pdf.set_draw_color(212, 175, 55)  # Gold accent line
        pdf.set_line_width(0.8)
        pdf.line(10, 25, 200, 25)
        pdf.ln(8)

        pdf.set_font("Helvetica", "", 12)
        fields = [
            ("Client Name", client_data.get("name", "N/A")),
            ("Age", f"{client_data.get('age', 'N/A')} years"),
            ("Height", f"{client_data.get('height', 'N/A')} cm"),
            ("Current Weight", f"{client_data.get('weight', 'N/A')} kg"),
            ("Enrolled Program", client_data.get("program", "N/A")),
            ("Daily Calorie Target", f"{client_data.get('calories', 'N/A')} kcal/day"),
            ("Target Weight Goal", f"{client_data.get('target_weight', 'N/A')} kg"),
            ("Target Adherence", f"{client_data.get('target_adherence', 'N/A')}%"),
            ("Membership Status", client_data.get("membership_status", "Active")),
            ("Membership Expiry", client_data.get("membership_expiry", "N/A"))
        ]

        for label, val in fields:
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(60, 8, f"{label}:", border=0)
            pdf.set_font("Helvetica", "", 11)
            pdf.cell(0, 8, str(val), ln=True)

        pdf.ln(5)
        pdf.set_font("Helvetica", "I", 10)
        pdf.multi_cell(0, 6, "Report generated automatically by ACEest DevOps Automated CI/CD Platform.")
        
        return bytes(pdf.output())
    except Exception:
        # Fallback to text bytes if fpdf is not present
        text = f"ACEEST FITNESS CLIENT REPORT\nName: {client_data.get('name')}\nProgram: {client_data.get('program')}\n"
        return text.encode("utf-8")
