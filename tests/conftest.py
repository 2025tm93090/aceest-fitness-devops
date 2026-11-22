"""
Pytest configuration and fixtures for ACEest Fitness testing.
"""
import os
import tempfile
import pytest
from app import create_app, models

@pytest.fixture
def app():
    # Create temporary database file for isolation
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    app = create_app({
        "TESTING": True,
        "DATABASE": db_path,
        "SECRET_KEY": "test-secret-key-123"
    })

    with app.app_context():
        models.init_db(db_path)

    yield app

    os.close(db_fd)
    try:
        os.unlink(db_path)
    except OSError:
        pass

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()
