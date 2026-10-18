from datetime import date, datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from .. import models
from ..crud import create_row, delete_row, get_or_404, list_rows, update_row
from ..database import get_db
from ..schemas.patients import (
    InsurancePolicyCreate,
    InsurancePolicyRead,
    InsurancePolicyUpdate,
    InsuranceProviderCreate,
    InsuranceProviderRead,
    InsuranceProviderUpdate,
    PatientCreate,
    PatientRead,
    PatientUpdate,
)
from ..security import get_current_staff, require_roles

router = APIRouter(tags=["patient"])


def date_of_birth_from_age(age: int) -> date:
    today = datetime.now().date()
    try:
        return today.replace(year=today.year - age)
    except ValueError:
        # 29 February, and the target year is not a leap year
        return today.replace(year=today.year - age, month=2, day=28)


def check_validity(valid_from: date, valid_to: date) -> None:
    if valid_to < valid_from:
        raise HTTPException(status_code=400, detail="valid_to cannot be before valid_from")


# ---------------------------------------------------------------- patients


@router.get("/patients", response_model=List[PatientRead], dependencies=[Depends(get_current_staff)])
def list_patients(
    phone: Optional[str] = None,
    name: Optional[str] = None,
    db: Session = Depends(get_db),
):
    stmt = select(models.Patient)
    if phone is not None:
        stmt = stmt.where(models.Patient.phone == phone)
    if name is not None:
        pattern = f"%{name}%"
        stmt = stmt.where(
            or_(
                models.Patient.first_name.ilike(pattern),
                models.Patient.last_name.ilike(pattern),
            )
        )
    stmt = stmt.order_by(models.Patient.id)
    return list(db.scalars(stmt).all())


@router.get(
    "/patients/{patient_id}",
    response_model=PatientRead,
    dependencies=[Depends(get_current_staff)],
)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, models.Patient, patient_id, "Patient")


@router.post(
    "/patients",
    response_model=PatientRead,
    status_code=201,
    dependencies=[Depends(require_roles("receptionist"))],
)
def create_patient(payload: PatientCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    age = data.pop("age")
    data["date_of_birth"] = date_of_birth_from_age(age)
    return create_row(db, models.Patient, data)


@router.patch(
    "/patients/{patient_id}",
    response_model=PatientRead,
    dependencies=[Depends(require_roles("receptionist"))],
)
def update_patient(patient_id: int, payload: PatientUpdate, db: Session = Depends(get_db)):
    patient = get_or_404(db, models.Patient, patient_id, "Patient")
    data = payload.model_dump(exclude_unset=True)
    age = data.pop("age", None)
    if age is not None:
        data["date_of_birth"] = date_of_birth_from_age(age)
    return update_row(db, patient, data)


# ---------------------------------------------------------------- insurance providers


@router.get(
    "/insurance-providers",
    response_model=List[InsuranceProviderRead],
    dependencies=[Depends(get_current_staff)],
)
def list_insurance_providers(db: Session = Depends(get_db)):
    return list_rows(db, models.InsuranceProvider)


@router.get(
    "/insurance-providers/{provider_id}",
    response_model=InsuranceProviderRead,
    dependencies=[Depends(get_current_staff)],
)
def get_insurance_provider(provider_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, models.InsuranceProvider, provider_id, "Insurance provider")


@router.post(
    "/insurance-providers",
    response_model=InsuranceProviderRead,
    status_code=201,
    dependencies=[Depends(require_roles("admin"))],
)
def create_insurance_provider(payload: InsuranceProviderCreate, db: Session = Depends(get_db)):
    return create_row(db, models.InsuranceProvider, payload.model_dump())


@router.patch(
    "/insurance-providers/{provider_id}",
    response_model=InsuranceProviderRead,
    dependencies=[Depends(require_roles("admin"))],
)
def update_insurance_provider(
    provider_id: int, payload: InsuranceProviderUpdate, db: Session = Depends(get_db)
):
    provider = get_or_404(db, models.InsuranceProvider, provider_id, "Insurance provider")
    return update_row(db, provider, payload.model_dump(exclude_unset=True))


@router.delete(
    "/insurance-providers/{provider_id}",
    status_code=204,
    dependencies=[Depends(require_roles("admin"))],
)
def delete_insurance_provider(provider_id: int, db: Session = Depends(get_db)) -> None:
    provider = get_or_404(db, models.InsuranceProvider, provider_id, "Insurance provider")
    delete_row(db, provider)


# ---------------------------------------------------------------- insurance policies


@router.get(
    "/insurance-policies",
    response_model=List[InsurancePolicyRead],
    dependencies=[Depends(get_current_staff)],
)
def list_insurance_policies(patient_id: Optional[int] = None, db: Session = Depends(get_db)):
    return list_rows(db, models.InsurancePolicy, patient_id=patient_id)


@router.get(
    "/insurance-policies/{policy_id}",
    response_model=InsurancePolicyRead,
    dependencies=[Depends(get_current_staff)],
)
def get_insurance_policy(policy_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, models.InsurancePolicy, policy_id, "Insurance policy")


@router.post(
    "/insurance-policies",
    response_model=InsurancePolicyRead,
    status_code=201,
    dependencies=[Depends(require_roles("receptionist"))],
)
def create_insurance_policy(payload: InsurancePolicyCreate, db: Session = Depends(get_db)):
    get_or_404(db, models.Patient, payload.patient_id, "Patient")
    get_or_404(db, models.InsuranceProvider, payload.provider_id, "Insurance provider")
    check_validity(payload.valid_from, payload.valid_to)
    return create_row(db, models.InsurancePolicy, payload.model_dump())


@router.patch(
    "/insurance-policies/{policy_id}",
    response_model=InsurancePolicyRead,
    dependencies=[Depends(require_roles("receptionist"))],
)
def update_insurance_policy(
    policy_id: int, payload: InsurancePolicyUpdate, db: Session = Depends(get_db)
):
    policy = get_or_404(db, models.InsurancePolicy, policy_id, "Insurance policy")
    data = payload.model_dump(exclude_unset=True)
    valid_from = data.get("valid_from") or policy.valid_from
    valid_to = data.get("valid_to") or policy.valid_to
    check_validity(valid_from, valid_to)
    return update_row(db, policy, data)
