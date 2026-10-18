"""Load CSV files into the database: one file per table, named <table>.csv (department.csv, bed_assignment.csv, ...).

Usage from backend/:
    .venv/bin/python seed_csv.py [folder] [--password PW]

    folder        optional; defaults to the repo's data/ folder.
    --password PW optional; every staff row that has a username gets password_hash = hash_password(PW),
                  replacing whatever the CSV had.

created_at and updated_at columns are loaded when they have a value and left to the default when empty.
Rows are inserted straight into the DB, not through the API, so the API's ordering rules are not checked.
"""

import argparse
import csv
import sys
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Dict, Optional, Set, Tuple

from sqlalchemy import Boolean, Date, DateTime, Integer, Numeric
from sqlalchemy.exc import IntegrityError

from app import models  # noqa: F401  (imported so every model is registered on Base)
from app.database import Base, SessionLocal, engine
from app.routers.patients import date_of_birth_from_age
from app.security import hash_password

DEFAULT_FOLDER = Path(__file__).resolve().parent.parent / "data"
# Convenience columns that are not table columns; they are turned into real columns while loading.
EXTRA_COLUMNS: Dict[str, Set[str]] = {"staff": {"password"}, "patient": {"age"}}
TRUE_WORDS = ("true", "1", "yes")
FALSE_WORDS = ("false", "0", "no")


class SeedError(Exception):
    pass


def _allowed_headers(table) -> Set[str]:
    names = {column.name for column in table.columns}
    return names | EXTRA_COLUMNS.get(table.name, set())


def _convert(text: str, column):
    """Turn one non-empty cell into a Python value for the column. Raises ValueError or ArithmeticError if it does not fit."""
    if isinstance(column.type, Integer):
        return int(text)
    if isinstance(column.type, Numeric):
        return Decimal(text)
    if isinstance(column.type, DateTime):
        return datetime.fromisoformat(text)
    if isinstance(column.type, Date):
        return date.fromisoformat(text)
    if isinstance(column.type, Boolean):
        if text.lower() in TRUE_WORDS:
            return True
        if text.lower() in FALSE_WORDS:
            return False
        raise ValueError(text)
    return text


def _cell_value(file_name: str, row_no: int, column, text: str):
    try:
        return _convert(text, column)
    except (ValueError, ArithmeticError):
        raise SeedError(
            f"{file_name} row {row_no}: column '{column.name}': invalid value '{text}'"
        )


def _row_data(file_name: str, row_no: int, table, values: Dict[str, str], password: Optional[str]) -> dict:
    """Build the keyword arguments for the model from one row (values are already stripped)."""
    data = {}
    for column in table.columns:
        text = values.get(column.name, "")
        if text == "":
            continue
        data[column.name] = _cell_value(file_name, row_no, column, text)

    if table.name == "staff" and values.get("password"):
        data["password_hash"] = hash_password(values["password"])
    if table.name == "staff" and password is not None and values.get("username"):
        data["password_hash"] = hash_password(password)
    if table.name == "patient" and values.get("age") and "date_of_birth" not in data:
        try:
            data["date_of_birth"] = date_of_birth_from_age(int(values["age"]))
        except ValueError:
            raise SeedError(
                f"{file_name} row {row_no}: column 'age': invalid value '{values['age']}'"
            )
    return data


def _db_message(err: IntegrityError) -> str:
    return str(err.orig)


def _load_file(path: Path, table, model, session_factory, password: Optional[str]) -> Tuple[int, int]:
    inserted = 0
    skipped = 0
    session = session_factory()
    try:
        with path.open(newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            headers = [h.strip() for h in reader.fieldnames or []]
            reader.fieldnames = headers

            allowed = _allowed_headers(table)
            for header in headers:
                if header not in allowed:
                    raise SeedError(f"{path.name}: unknown column '{header}'")

            for row_no, row in enumerate(reader, start=2):  # header is row 1
                values = {header: (row.get(header) or "").strip() for header in headers}
                data = _row_data(path.name, row_no, table, values, password)
                if "id" in data and session.get(model, data["id"]) is not None:
                    skipped += 1
                    continue
                session.add(model(**data))
                try:
                    session.flush()
                except IntegrityError as err:
                    session.rollback()
                    raise SeedError(f"{path.name} row {row_no}: {_db_message(err)}") from err
                inserted += 1

        try:
            session.commit()
        except IntegrityError as err:
            session.rollback()
            raise SeedError(f"{path.name}: {_db_message(err)}") from err
    finally:
        session.close()
    return inserted, skipped


def load_folder(folder: Path, session_factory, password: Optional[str] = None) -> Dict[str, Tuple[int, int]]:
    """Load every <table>.csv in folder, in FK order. Returns table -> (inserted, skipped)."""
    model_by_table = {mapper.class_.__tablename__: mapper.class_ for mapper in Base.registry.mappers}

    for path in folder.glob("*.csv"):
        if path.stem not in model_by_table:
            raise SeedError(f"{path.name}: no table called '{path.stem}'")

    results: Dict[str, Tuple[int, int]] = {}
    for table in Base.metadata.sorted_tables:
        path = folder / (table.name + ".csv")
        if path.exists():
            results[table.name] = _load_file(
                path, table, model_by_table[table.name], session_factory, password
            )
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Load the CSV files into the database.")
    parser.add_argument("folder", nargs="?", default=str(DEFAULT_FOLDER), help="folder with <table>.csv files (default: data/)")
    parser.add_argument("--password", help="password for every staff member that has a username")
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)
    try:
        results = load_folder(Path(args.folder), SessionLocal, password=args.password)
    except SeedError as err:
        sys.exit(str(err))
    for table, (inserted, skipped) in results.items():
        print(f"{table}: {inserted} inserted, {skipped} skipped")


if __name__ == "__main__":
    main()
