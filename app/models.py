"""
Database models and data access layer for ACEest Fitness & Gym.
Supports SQLite with customizable connection for unit testing.
"""
import sqlite3
import os
from datetime import datetime, date

def get_connection(db_path=None):
    if not db_path:
        try:
            from flask import current_app
            if current_app and current_app.config.get("DATABASE"):
                db_path = current_app.config.get("DATABASE")
        except Exception:
            pass
    path = db_path or os.environ.get("ACEEST_DB_PATH", "aceest_fitness.db")
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path=None):
    conn = get_connection(db_path)
    cur = conn.cursor()

    # Users table (Role-Based Access)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'Trainer',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Clients table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            age INTEGER,
            height REAL,
            weight REAL,
            program TEXT NOT NULL,
            calories INTEGER,
            target_weight REAL,
            target_adherence INTEGER,
            membership_status TEXT DEFAULT 'Active',
            membership_expiry TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Weekly adherence progress
    cur.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            week TEXT NOT NULL,
            adherence INTEGER NOT NULL,
            logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_name) REFERENCES clients (name) ON DELETE CASCADE
        )
    """)

    # Workouts log
    cur.execute("""
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            date TEXT NOT NULL,
            workout_type TEXT NOT NULL,
            duration_min INTEGER NOT NULL DEFAULT 60,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (client_name) REFERENCES clients (name) ON DELETE CASCADE
        )
    """)

    # Exercises inside workouts
    cur.execute("""
        CREATE TABLE IF NOT EXISTS exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workout_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            sets INTEGER NOT NULL,
            reps INTEGER NOT NULL,
            weight REAL DEFAULT 0.0,
            FOREIGN KEY (workout_id) REFERENCES workouts (id) ON DELETE CASCADE
        )
    """)

    # Body metrics tracking
    cur.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            date TEXT NOT NULL,
            weight REAL,
            waist REAL,
            bodyfat REAL,
            FOREIGN KEY (client_name) REFERENCES clients (name) ON DELETE CASCADE
        )
    """)

    # Default admin user seed
    cur.execute("SELECT id FROM users WHERE username = 'admin'")
    if not cur.fetchone():
        cur.execute("""
            INSERT INTO users (username, password, role)
            VALUES ('admin', 'admin123', 'Admin')
        """)

    conn.commit()
    conn.close()

def get_all_clients(db_path=None):
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM clients ORDER BY name ASC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def get_client_by_name(name, db_path=None):
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM clients WHERE name = ?", (name,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def save_client(client_data, db_path=None):
    conn = get_connection(db_path)
    cur = conn.cursor()
    name = client_data.get("name", "").strip()
    age = client_data.get("age")
    height = client_data.get("height")
    weight = client_data.get("weight")
    program = client_data.get("program", "Beginner (BG)")
    calories = client_data.get("calories")
    target_weight = client_data.get("target_weight")
    target_adherence = client_data.get("target_adherence", 80)
    membership_status = client_data.get("membership_status", "Active")
    membership_expiry = client_data.get("membership_expiry", "")
    notes = client_data.get("notes", "")

    cur.execute("""
        INSERT INTO clients (name, age, height, weight, program, calories, target_weight,
                             target_adherence, membership_status, membership_expiry, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
            age = excluded.age,
            height = excluded.height,
            weight = excluded.weight,
            program = excluded.program,
            calories = excluded.calories,
            target_weight = excluded.target_weight,
            target_adherence = excluded.target_adherence,
            membership_status = excluded.membership_status,
            membership_expiry = excluded.membership_expiry,
            notes = excluded.notes
    """, (name, age, height, weight, program, calories, target_weight,
          target_adherence, membership_status, membership_expiry, notes))
    
    conn.commit()
    conn.close()
    return get_client_by_name(name, db_path)

def delete_client(name, db_path=None):
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("DELETE FROM clients WHERE name = ?", (name,))
    deleted = cur.rowcount > 0
    cur.execute("DELETE FROM progress WHERE client_name = ?", (name,))
    cur.execute("DELETE FROM workouts WHERE client_name = ?", (name,))
    cur.execute("DELETE FROM metrics WHERE client_name = ?", (name,))
    conn.commit()
    conn.close()
    return deleted

def log_progress(client_name, adherence, week=None, db_path=None):
    if not week:
        week = datetime.now().strftime("Week %U - %Y")
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO progress (client_name, week, adherence)
        VALUES (?, ?, ?)
    """, (client_name, week, adherence))
    conn.commit()
    log_id = cur.lastrowid
    conn.close()
    return log_id

def get_progress_by_client(client_name, db_path=None):
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM progress WHERE client_name = ? ORDER BY id ASC
    """, (client_name,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def log_workout(workout_data, exercises=None, db_path=None):
    conn = get_connection(db_path)
    cur = conn.cursor()
    w_date = workout_data.get("date", date.today().isoformat())
    client_name = workout_data.get("client_name")
    workout_type = workout_data.get("workout_type", "Strength")
    duration_min = workout_data.get("duration_min", 60)
    notes = workout_data.get("notes", "")

    cur.execute("""
        INSERT INTO workouts (client_name, date, workout_type, duration_min, notes)
        VALUES (?, ?, ?, ?, ?)
    """, (client_name, w_date, workout_type, duration_min, notes))
    workout_id = cur.lastrowid

    if exercises and isinstance(exercises, list):
        for ex in exercises:
            cur.execute("""
                INSERT INTO exercises (workout_id, name, sets, reps, weight)
                VALUES (?, ?, ?, ?, ?)
            """, (workout_id, ex.get("name", "Exercise"), ex.get("sets", 3),
                  ex.get("reps", 10), ex.get("weight", 0.0)))

    conn.commit()
    conn.close()
    return workout_id

def get_workouts_by_client(client_name, db_path=None):
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM workouts WHERE client_name = ? ORDER BY date DESC, id DESC
    """, (client_name,))
    workouts = [dict(r) for r in cur.fetchall()]
    for w in workouts:
        cur.execute("SELECT * FROM exercises WHERE workout_id = ?", (w["id"],))
        w["exercises"] = [dict(e) for e in cur.fetchall()]
    conn.close()
    return workouts

def log_metric(metric_data, db_path=None):
    conn = get_connection(db_path)
    cur = conn.cursor()
    m_date = metric_data.get("date", date.today().isoformat())
    client_name = metric_data.get("client_name")
    weight = metric_data.get("weight")
    waist = metric_data.get("waist")
    bodyfat = metric_data.get("bodyfat")

    cur.execute("""
        INSERT INTO metrics (client_name, date, weight, waist, bodyfat)
        VALUES (?, ?, ?, ?, ?)
    """, (client_name, m_date, weight, waist, bodyfat))
    conn.commit()
    metric_id = cur.lastrowid
    conn.close()
    return metric_id

def get_metrics_by_client(client_name, db_path=None):
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM metrics WHERE client_name = ? ORDER BY date ASC
    """, (client_name,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def verify_user(username, password, db_path=None):
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id, username, role FROM users WHERE username = ? AND password = ?", (username, password))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None
