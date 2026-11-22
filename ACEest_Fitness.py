"""
ACEest Fitness & Gym Management System
Main Entrypoint for the Flask Application (Assignment 2 DevOps Implementation)
Company: ACEest Fitness & Gym
"""
import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1")
    print(f"[*] Starting ACEest Fitness Web Application on http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)
