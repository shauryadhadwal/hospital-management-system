"""Create the tables and the first admin login.

Run from the backend/ folder:  python seed.py
"""

from datetime import date

from sqlalchemy import select

from app import models
from app.database import Base, SessionLocal, engine
from app.security import hash_password

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"
ADMIN_DEPARTMENT = "Administration"


def main() -> None:
    Base.metadata.create_all(bind=engine)
    print("Tables created (or already present).")

    db = SessionLocal()
    try:
        existing = db.scalar(select(models.Staff).where(models.Staff.username == ADMIN_USERNAME))
        if existing is not None:
            print(f"Staff with username '{ADMIN_USERNAME}' already exists; nothing to do.")
            return

        dept = db.scalar(select(models.Department).where(models.Department.name == ADMIN_DEPARTMENT))
        if dept is None:
            dept = models.Department(name=ADMIN_DEPARTMENT)
            db.add(dept)
            db.flush()
            print(f"Created department '{ADMIN_DEPARTMENT}'.")
        else:
            print(f"Department '{ADMIN_DEPARTMENT}' already exists.")

        admin = models.Staff(
            department_id=dept.id,
            first_name="Admin",
            last_name="User",
            role="admin",
            hire_date=date.today(),
            username=ADMIN_USERNAME,
            password_hash=hash_password(ADMIN_PASSWORD),
            login_enabled=True,
        )
        db.add(admin)
        db.commit()
        print(f"Created staff 'Admin User' (username '{ADMIN_USERNAME}', password '{ADMIN_PASSWORD}').")
    finally:
        db.close()


if __name__ == "__main__":
    main()
