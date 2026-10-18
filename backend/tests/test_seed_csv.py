import csv
from datetime import date, datetime
from pathlib import Path

import bcrypt
import pytest
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import sessionmaker

from app import models
from app.database import Base
from app.security import verify_password
from seed_csv import SeedError, load_folder

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def _new_factory(tmp_path, foreign_keys=False):
    engine = create_engine(f"sqlite:///{tmp_path / 'seed.db'}")
    if foreign_keys:
        @event.listens_for(engine, "connect")
        def _enable_foreign_keys(dbapi_connection, _record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)


def _data_row_count(path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        return sum(1 for _ in csv.DictReader(f))


def test_repo_data_loads_and_is_rerunnable(tmp_path):
    factory = _new_factory(tmp_path, foreign_keys=True)

    results = load_folder(DATA_DIR, factory)

    csv_tables = {path.stem for path in DATA_DIR.glob("*.csv")}
    assert set(results) == csv_tables
    for table in csv_tables:
        expected = _data_row_count(DATA_DIR / f"{table}.csv")
        assert results[table] == (expected, 0), table

    with factory() as session:
        staff = session.get(models.Staff, 1)
        assert staff.created_at == datetime(2026, 1, 5, 9, 0)

    again = load_folder(DATA_DIR, factory)
    assert again == {table: (0, inserted) for table, (inserted, _) in results.items()}


def test_password_flag_sets_password_for_staff_with_username(tmp_path):
    factory = _new_factory(tmp_path)

    load_folder(DATA_DIR, factory, password="test-pass")

    with factory() as session:
        meera = session.scalars(
            select(models.Staff).where(models.Staff.username == "reception.meera")
        ).one()
        assert verify_password("test-pass", meera.password_hash)


def test_verify_password_accepts_bcrypt_hash():
    hashed = bcrypt.hashpw(b"x", bcrypt.gensalt(rounds=4)).decode("utf-8")

    assert verify_password("x", hashed)
    assert not verify_password("y", hashed)


def test_unknown_column_is_rejected(tmp_path):
    folder = tmp_path / "bad"
    folder.mkdir()
    (folder / "department.csv").write_text("id,name,colour\n1,Administration,blue\n", encoding="utf-8")

    with pytest.raises(SeedError) as excinfo:
        load_folder(folder, _new_factory(tmp_path))
    assert "colour" in str(excinfo.value)


def test_age_becomes_date_of_birth(tmp_path):
    folder = tmp_path / "patients"
    folder.mkdir()
    (folder / "patient.csv").write_text(
        "first_name,last_name,age,sex,phone\nPeehu,Sharma,30,female,9000000001\n",
        encoding="utf-8",
    )
    factory = _new_factory(tmp_path)

    results = load_folder(folder, factory)
    assert results == {"patient": (1, 0)}

    with factory() as session:
        patient = session.scalars(select(models.Patient)).one()
        assert patient.date_of_birth.year == date.today().year - 30
