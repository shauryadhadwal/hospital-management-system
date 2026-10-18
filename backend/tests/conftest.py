import os
from datetime import date
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

TEST_DB_NAME = "test_hospital.db"
BACKEND_DIR = Path(__file__).resolve().parent.parent

# Must be set before the app is imported, because database.py reads it at import time.
os.environ["HOSPITAL_DB_URL"] = "sqlite:///./test_hospital.db"


def _remove_test_db():
    test_db_file = BACKEND_DIR / TEST_DB_NAME
    if test_db_file.exists():
        test_db_file.unlink()


_remove_test_db()

from app import models  # noqa: E402
from app.database import SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.security import hash_password  # noqa: E402


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:  # lifespan creates the tables
        db = SessionLocal()
        try:
            # Same admin login as seed.py
            dept = models.Department(name="Administration")
            db.add(dept)
            db.flush()
            db.add(
                models.Staff(
                    department_id=dept.id,
                    first_name="Admin",
                    last_name="User",
                    role="admin",
                    hire_date=date.today(),
                    username="admin",
                    password_hash=hash_password("admin123"),
                    login_enabled=True,
                )
            )
            db.commit()
        finally:
            db.close()
        yield c
    engine.dispose()
    _remove_test_db()


@pytest.fixture(scope="session")
def login():
    def _login(client, username, password):
        r = client.post("/auth/login", data={"username": username, "password": password})
        assert r.status_code == 200, r.text
        return {"Authorization": "Bearer " + r.json()["access_token"]}

    return _login
