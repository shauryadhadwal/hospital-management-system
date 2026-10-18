from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models
from ..crud import create_row, delete_row, get_or_404, list_rows, update_row
from ..database import get_db
from ..schemas.ref import (
    ConsumableCreate,
    ConsumableRead,
    ConsumableUpdate,
    LabTestCreate,
    LabTestRead,
    LabTestUpdate,
    MedicationCreate,
    MedicationRead,
    MedicationUpdate,
    ProcedureCreate,
    ProcedureRead,
    ProcedureUpdate,
)
from ..security import get_current_staff, require_roles

router = APIRouter(tags=["ref"])


# ---------------------------------------------------------------- procedures


@router.get("/procedures", response_model=List[ProcedureRead], dependencies=[Depends(get_current_staff)])
def list_procedures(db: Session = Depends(get_db)):
    return list_rows(db, models.Procedure)


@router.get("/procedures/{id}", response_model=ProcedureRead, dependencies=[Depends(get_current_staff)])
def get_procedure(id: int, db: Session = Depends(get_db)):
    return get_or_404(db, models.Procedure, id)


@router.post(
    "/procedures",
    response_model=ProcedureRead,
    status_code=201,
    dependencies=[Depends(require_roles("admin"))],
)
def create_procedure(payload: ProcedureCreate, db: Session = Depends(get_db)):
    return create_row(db, models.Procedure, payload.model_dump())


@router.patch("/procedures/{id}", response_model=ProcedureRead, dependencies=[Depends(require_roles("admin"))])
def update_procedure(id: int, payload: ProcedureUpdate, db: Session = Depends(get_db)):
    obj = get_or_404(db, models.Procedure, id)
    return update_row(db, obj, payload.model_dump(exclude_unset=True))


@router.delete("/procedures/{id}", status_code=204, dependencies=[Depends(require_roles("admin"))])
def delete_procedure(id: int, db: Session = Depends(get_db)):
    obj = get_or_404(db, models.Procedure, id)
    delete_row(db, obj)


# ---------------------------------------------------------------- medications


@router.get("/medications", response_model=List[MedicationRead], dependencies=[Depends(get_current_staff)])
def list_medications(db: Session = Depends(get_db)):
    return list_rows(db, models.Medication)


@router.get("/medications/{id}", response_model=MedicationRead, dependencies=[Depends(get_current_staff)])
def get_medication(id: int, db: Session = Depends(get_db)):
    return get_or_404(db, models.Medication, id)


@router.post(
    "/medications",
    response_model=MedicationRead,
    status_code=201,
    dependencies=[Depends(require_roles("admin"))],
)
def create_medication(payload: MedicationCreate, db: Session = Depends(get_db)):
    return create_row(db, models.Medication, payload.model_dump())


@router.patch("/medications/{id}", response_model=MedicationRead, dependencies=[Depends(require_roles("admin"))])
def update_medication(id: int, payload: MedicationUpdate, db: Session = Depends(get_db)):
    obj = get_or_404(db, models.Medication, id)
    return update_row(db, obj, payload.model_dump(exclude_unset=True))


@router.delete("/medications/{id}", status_code=204, dependencies=[Depends(require_roles("admin"))])
def delete_medication(id: int, db: Session = Depends(get_db)):
    obj = get_or_404(db, models.Medication, id)
    delete_row(db, obj)


# ---------------------------------------------------------------- lab tests


@router.get("/lab-tests", response_model=List[LabTestRead], dependencies=[Depends(get_current_staff)])
def list_lab_tests(db: Session = Depends(get_db)):
    return list_rows(db, models.LabTest)


@router.get("/lab-tests/{id}", response_model=LabTestRead, dependencies=[Depends(get_current_staff)])
def get_lab_test(id: int, db: Session = Depends(get_db)):
    return get_or_404(db, models.LabTest, id)


@router.post(
    "/lab-tests",
    response_model=LabTestRead,
    status_code=201,
    dependencies=[Depends(require_roles("admin"))],
)
def create_lab_test(payload: LabTestCreate, db: Session = Depends(get_db)):
    return create_row(db, models.LabTest, payload.model_dump())


@router.patch("/lab-tests/{id}", response_model=LabTestRead, dependencies=[Depends(require_roles("admin"))])
def update_lab_test(id: int, payload: LabTestUpdate, db: Session = Depends(get_db)):
    obj = get_or_404(db, models.LabTest, id)
    return update_row(db, obj, payload.model_dump(exclude_unset=True))


@router.delete("/lab-tests/{id}", status_code=204, dependencies=[Depends(require_roles("admin"))])
def delete_lab_test(id: int, db: Session = Depends(get_db)):
    obj = get_or_404(db, models.LabTest, id)
    delete_row(db, obj)


# ---------------------------------------------------------------- consumables


@router.get("/consumables", response_model=List[ConsumableRead], dependencies=[Depends(get_current_staff)])
def list_consumables(db: Session = Depends(get_db)):
    return list_rows(db, models.Consumable)


@router.get("/consumables/{id}", response_model=ConsumableRead, dependencies=[Depends(get_current_staff)])
def get_consumable(id: int, db: Session = Depends(get_db)):
    return get_or_404(db, models.Consumable, id)


@router.post(
    "/consumables",
    response_model=ConsumableRead,
    status_code=201,
    dependencies=[Depends(require_roles("admin"))],
)
def create_consumable(payload: ConsumableCreate, db: Session = Depends(get_db)):
    return create_row(db, models.Consumable, payload.model_dump())


@router.patch("/consumables/{id}", response_model=ConsumableRead, dependencies=[Depends(require_roles("admin"))])
def update_consumable(id: int, payload: ConsumableUpdate, db: Session = Depends(get_db)):
    obj = get_or_404(db, models.Consumable, id)
    return update_row(db, obj, payload.model_dump(exclude_unset=True))


@router.delete("/consumables/{id}", status_code=204, dependencies=[Depends(require_roles("admin"))])
def delete_consumable(id: int, db: Session = Depends(get_db)):
    obj = get_or_404(db, models.Consumable, id)
    delete_row(db, obj)
