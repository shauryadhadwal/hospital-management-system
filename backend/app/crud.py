from typing import Any, List, Optional, Type

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


def get_or_404(db: Session, Model: Type[Any], id: int, name: Optional[str] = None) -> Any:
    obj = db.get(Model, id)
    if obj is None:
        label = name or Model.__name__
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{label} {id} not found")
    return obj


def list_rows(db: Session, Model: Type[Any], **filters: Any) -> List[Any]:
    stmt = select(Model)
    for key, value in filters.items():
        if value is not None:
            stmt = stmt.where(getattr(Model, key) == value)
    stmt = stmt.order_by(Model.id)
    return list(db.scalars(stmt).all())


def commit_or_409(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        detail = str(getattr(exc, "orig", None) or exc)
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)


def create_row(db: Session, Model: Type[Any], data: dict) -> Any:
    obj = Model(**data)
    db.add(obj)
    commit_or_409(db)
    db.refresh(obj)
    return obj


def update_row(db: Session, obj: Any, data: dict) -> Any:
    for key, value in data.items():
        setattr(obj, key, value)
    commit_or_409(db)
    db.refresh(obj)
    return obj


def delete_row(db: Session, obj: Any) -> None:
    db.delete(obj)
    commit_or_409(db)
