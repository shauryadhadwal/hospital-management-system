from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models
from ..crud import commit_or_409, create_row, get_or_404, list_rows, update_row
from ..database import get_db
from ..schemas.clinical import (
    AtTime,
    BedAssignmentCreate,
    BedAssignmentRead,
    BedTransfer,
    ConsumableUsageCreate,
    ConsumableUsageRead,
    DiagnosisCreate,
    DiagnosisRead,
    DiagnosisUpdate,
    LabOrderCreate,
    LabOrderRead,
    LabOrderStatus,
    LabResultCreate,
    LabResultRead,
    PrescriptionCreate,
    PrescriptionRead,
    PrescriptionUpdate,
    ProcedureHistoryCreate,
    ProcedureHistoryRead,
    VisitCreate,
    VisitRead,
    VisitStatus,
    VisitUpdate,
    VitalSignCreate,
    VitalSignRead,
)
from ..security import get_current_doctor, get_current_staff, require_roles

router = APIRouter(tags=["clinical"])

MEASUREMENTS = (
    "temperature_c",
    "pulse_bpm",
    "systolic_bp",
    "diastolic_bp",
    "respiratory_rate",
    "oxygen_saturation",
)


def or_now(value: Optional[datetime]) -> datetime:
    return value if value is not None else datetime.now()


def time_or_now(payload: Optional[AtTime]) -> datetime:
    return or_now(payload.at if payload is not None else None)


def require_in_progress(visit: models.Visit) -> None:
    if visit.status != "in progress":
        raise HTTPException(
            status_code=400,
            detail=f"Visit {visit.id} is '{visit.status}', it must be 'in progress'",
        )


def open_stay_for_visit(db: Session, visit_id: int) -> Optional[models.BedAssignment]:
    return db.scalar(
        select(models.BedAssignment).where(
            models.BedAssignment.visit_id == visit_id,
            models.BedAssignment.end_time.is_(None),
        )
    )


def open_stay_for_bed(db: Session, bed_id: int) -> Optional[models.BedAssignment]:
    return db.scalar(
        select(models.BedAssignment).where(
            models.BedAssignment.bed_id == bed_id,
            models.BedAssignment.end_time.is_(None),
        )
    )


# ---------------------------------------------------------------- visits


@router.get("/visits", response_model=List[VisitRead], dependencies=[Depends(get_current_staff)])
def list_visits(
    patient_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    status: Optional[VisitStatus] = None,
    db: Session = Depends(get_db),
):
    return list_rows(db, models.Visit, patient_id=patient_id, doctor_id=doctor_id, status=status)


@router.get(
    "/visits/{visit_id}",
    response_model=VisitRead,
    dependencies=[Depends(get_current_staff)],
)
def get_visit(visit_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, models.Visit, visit_id, "Visit")


@router.post(
    "/visits",
    response_model=VisitRead,
    status_code=201,
    dependencies=[Depends(require_roles("receptionist"))],
)
def create_visit(payload: VisitCreate, db: Session = Depends(get_db)):
    get_or_404(db, models.Patient, payload.patient_id, "Patient")
    get_or_404(db, models.Doctor, payload.doctor_id, "Doctor")
    get_or_404(db, models.Department, payload.department_id, "Department")
    data = payload.model_dump()
    data["status"] = "booked"
    return create_row(db, models.Visit, data)


@router.post(
    "/visits/{visit_id}/check-in",
    response_model=VisitRead,
    dependencies=[Depends(require_roles("receptionist", "nurse"))],
)
def check_in_visit(visit_id: int, payload: Optional[AtTime] = None, db: Session = Depends(get_db)):
    visit = get_or_404(db, models.Visit, visit_id, "Visit")
    if visit.status != "booked":
        raise HTTPException(
            status_code=400,
            detail=f"Visit {visit.id} is '{visit.status}', only a 'booked' visit can be checked in",
        )
    return update_row(
        db,
        visit,
        {"status": "in progress", "actual_start": time_or_now(payload)},
    )


@router.patch(
    "/visits/{visit_id}",
    response_model=VisitRead,
    dependencies=[Depends(require_roles("doctor"))],
)
def update_visit(visit_id: int, payload: VisitUpdate, db: Session = Depends(get_db)):
    visit = get_or_404(db, models.Visit, visit_id, "Visit")
    require_in_progress(visit)
    return update_row(db, visit, payload.model_dump(exclude_unset=True))


@router.post(
    "/visits/{visit_id}/discharge",
    response_model=VisitRead,
    dependencies=[Depends(require_roles("doctor"))],
)
def discharge_visit(visit_id: int, payload: Optional[AtTime] = None, db: Session = Depends(get_db)):
    visit = get_or_404(db, models.Visit, visit_id, "Visit")
    require_in_progress(visit)
    at = time_or_now(payload)
    # Close the open bed stay first, then complete the visit (ordering rule 1).
    stay = open_stay_for_visit(db, visit.id)
    if stay is not None:
        stay.end_time = at
    visit.status = "completed"
    visit.actual_end = at
    commit_or_409(db)
    db.refresh(visit)
    return visit


# ---------------------------------------------------------------- bed assignments


@router.get(
    "/bed-assignments",
    response_model=List[BedAssignmentRead],
    dependencies=[Depends(get_current_staff)],
)
def list_bed_assignments(
    visit_id: Optional[int] = None,
    bed_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    return list_rows(db, models.BedAssignment, visit_id=visit_id, bed_id=bed_id)


@router.get(
    "/bed-assignments/{stay_id}",
    response_model=BedAssignmentRead,
    dependencies=[Depends(get_current_staff)],
)
def get_bed_assignment(stay_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, models.BedAssignment, stay_id, "Bed assignment")


@router.post(
    "/bed-assignments",
    response_model=BedAssignmentRead,
    status_code=201,
    dependencies=[Depends(require_roles("receptionist", "nurse"))],
)
def create_bed_assignment(payload: BedAssignmentCreate, db: Session = Depends(get_db)):
    visit = get_or_404(db, models.Visit, payload.visit_id, "Visit")
    get_or_404(db, models.Bed, payload.bed_id, "Bed")
    require_in_progress(visit)
    if visit.visit_type != "inpatient":
        raise HTTPException(
            status_code=400,
            detail=f"Visit {visit.id} is '{visit.visit_type}', beds are only for inpatient visits",
        )
    if open_stay_for_bed(db, payload.bed_id) is not None:
        raise HTTPException(status_code=400, detail=f"Bed {payload.bed_id} is occupied")
    if open_stay_for_visit(db, visit.id) is not None:
        raise HTTPException(status_code=400, detail=f"Visit {visit.id} already has an open bed stay")
    return create_row(
        db,
        models.BedAssignment,
        {
            "visit_id": payload.visit_id,
            "bed_id": payload.bed_id,
            "start_time": or_now(payload.start_time),
        },
    )


@router.post(
    "/bed-assignments/{stay_id}/transfer",
    response_model=BedAssignmentRead,
    status_code=201,
    dependencies=[Depends(require_roles("receptionist", "nurse"))],
)
def transfer_bed_assignment(stay_id: int, payload: BedTransfer, db: Session = Depends(get_db)):
    stay = get_or_404(db, models.BedAssignment, stay_id, "Bed assignment")
    if stay.end_time is not None:
        raise HTTPException(status_code=400, detail=f"Bed assignment {stay.id} is already closed")
    get_or_404(db, models.Bed, payload.bed_id, "Bed")
    if open_stay_for_bed(db, payload.bed_id) is not None:
        raise HTTPException(status_code=400, detail=f"Bed {payload.bed_id} is occupied")
    at = time_or_now(payload)
    stay.end_time = at
    new_stay = models.BedAssignment(visit_id=stay.visit_id, bed_id=payload.bed_id, start_time=at)
    db.add(new_stay)
    commit_or_409(db)
    db.refresh(new_stay)
    return new_stay


# ---------------------------------------------------------------- diagnoses


@router.get(
    "/diagnoses",
    response_model=List[DiagnosisRead],
    dependencies=[Depends(get_current_staff)],
)
def list_diagnoses(visit_id: Optional[int] = None, db: Session = Depends(get_db)):
    return list_rows(db, models.Diagnosis, visit_id=visit_id)


@router.get(
    "/diagnoses/{diagnosis_id}",
    response_model=DiagnosisRead,
    dependencies=[Depends(get_current_staff)],
)
def get_diagnosis(diagnosis_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, models.Diagnosis, diagnosis_id, "Diagnosis")


@router.post(
    "/diagnoses",
    response_model=DiagnosisRead,
    status_code=201,
    dependencies=[Depends(require_roles("doctor"))],
)
def create_diagnosis(payload: DiagnosisCreate, db: Session = Depends(get_db)):
    visit = get_or_404(db, models.Visit, payload.visit_id, "Visit")
    require_in_progress(visit)
    return create_row(db, models.Diagnosis, payload.model_dump())


@router.patch(
    "/diagnoses/{diagnosis_id}",
    response_model=DiagnosisRead,
    dependencies=[Depends(require_roles("doctor"))],
)
def update_diagnosis(diagnosis_id: int, payload: DiagnosisUpdate, db: Session = Depends(get_db)):
    diagnosis = get_or_404(db, models.Diagnosis, diagnosis_id, "Diagnosis")
    return update_row(db, diagnosis, payload.model_dump(exclude_unset=True))


# ---------------------------------------------------------------- procedure history


@router.get(
    "/procedure-history",
    response_model=List[ProcedureHistoryRead],
    dependencies=[Depends(get_current_staff)],
)
def list_procedure_history(visit_id: Optional[int] = None, db: Session = Depends(get_db)):
    return list_rows(db, models.ProcedureHistory, visit_id=visit_id)


@router.get(
    "/procedure-history/{procedure_history_id}",
    response_model=ProcedureHistoryRead,
    dependencies=[Depends(get_current_staff)],
)
def get_procedure_history(procedure_history_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, models.ProcedureHistory, procedure_history_id, "Procedure history")


@router.post(
    "/procedure-history",
    response_model=ProcedureHistoryRead,
    status_code=201,
    dependencies=[Depends(require_roles("doctor"))],
)
def create_procedure_history(
    payload: ProcedureHistoryCreate,
    doctor: models.Doctor = Depends(get_current_doctor),
    db: Session = Depends(get_db),
):
    visit = get_or_404(db, models.Visit, payload.visit_id, "Visit")
    get_or_404(db, models.Procedure, payload.procedure_id, "Procedure")
    require_in_progress(visit)
    return create_row(
        db,
        models.ProcedureHistory,
        {
            "visit_id": payload.visit_id,
            "procedure_id": payload.procedure_id,
            "performed_at": or_now(payload.performed_at),
            "performed_by": doctor.id,
        },
    )


# ---------------------------------------------------------------- prescriptions


@router.get(
    "/prescriptions",
    response_model=List[PrescriptionRead],
    dependencies=[Depends(get_current_staff)],
)
def list_prescriptions(visit_id: Optional[int] = None, db: Session = Depends(get_db)):
    return list_rows(db, models.Prescription, visit_id=visit_id)


@router.get(
    "/prescriptions/{prescription_id}",
    response_model=PrescriptionRead,
    dependencies=[Depends(get_current_staff)],
)
def get_prescription(prescription_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, models.Prescription, prescription_id, "Prescription")


@router.post(
    "/prescriptions",
    response_model=PrescriptionRead,
    status_code=201,
    dependencies=[Depends(require_roles("doctor"))],
)
def create_prescription(payload: PrescriptionCreate, db: Session = Depends(get_db)):
    visit = get_or_404(db, models.Visit, payload.visit_id, "Visit")
    get_or_404(db, models.Medication, payload.medication_id, "Medication")
    require_in_progress(visit)
    return create_row(db, models.Prescription, payload.model_dump())


@router.patch(
    "/prescriptions/{prescription_id}",
    response_model=PrescriptionRead,
    dependencies=[Depends(require_roles("doctor"))],
)
def update_prescription(
    prescription_id: int, payload: PrescriptionUpdate, db: Session = Depends(get_db)
):
    prescription = get_or_404(db, models.Prescription, prescription_id, "Prescription")
    return update_row(db, prescription, payload.model_dump(exclude_unset=True))


# ---------------------------------------------------------------- lab orders


@router.get(
    "/lab-orders",
    response_model=List[LabOrderRead],
    dependencies=[Depends(get_current_staff)],
)
def list_lab_orders(
    visit_id: Optional[int] = None,
    status: Optional[LabOrderStatus] = None,
    db: Session = Depends(get_db),
):
    return list_rows(db, models.LabOrder, visit_id=visit_id, status=status)


@router.get(
    "/lab-orders/{lab_order_id}",
    response_model=LabOrderRead,
    dependencies=[Depends(get_current_staff)],
)
def get_lab_order(lab_order_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, models.LabOrder, lab_order_id, "Lab order")


@router.post(
    "/lab-orders",
    response_model=LabOrderRead,
    status_code=201,
    dependencies=[Depends(require_roles("doctor"))],
)
def create_lab_order(
    payload: LabOrderCreate,
    doctor: models.Doctor = Depends(get_current_doctor),
    db: Session = Depends(get_db),
):
    visit = get_or_404(db, models.Visit, payload.visit_id, "Visit")
    get_or_404(db, models.LabTest, payload.lab_test_id, "Lab test")
    require_in_progress(visit)
    return create_row(
        db,
        models.LabOrder,
        {
            "visit_id": payload.visit_id,
            "lab_test_id": payload.lab_test_id,
            "ordered_at": or_now(payload.ordered_at),
            "ordered_by": doctor.id,
            "status": "ordered",
        },
    )


# ---------------------------------------------------------------- lab results


@router.get(
    "/lab-results",
    response_model=List[LabResultRead],
    dependencies=[Depends(get_current_staff)],
)
def list_lab_results(lab_order_id: Optional[int] = None, db: Session = Depends(get_db)):
    return list_rows(db, models.LabResult, lab_order_id=lab_order_id)


@router.get(
    "/lab-results/{lab_result_id}",
    response_model=LabResultRead,
    dependencies=[Depends(get_current_staff)],
)
def get_lab_result(lab_result_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, models.LabResult, lab_result_id, "Lab result")


@router.post(
    "/lab-results",
    response_model=LabResultRead,
    status_code=201,
)
def create_lab_result(
    payload: LabResultCreate,
    staff: models.Staff = Depends(require_roles("lab")),
    db: Session = Depends(get_db),
):
    order = get_or_404(db, models.LabOrder, payload.lab_order_id, "Lab order")
    if order.status != "ordered":
        raise HTTPException(
            status_code=400,
            detail=f"Lab order {order.id} is '{order.status}', it must be 'ordered'",
        )
    result = models.LabResult(
        lab_order_id=payload.lab_order_id,
        result_text=payload.result_text,
        resulted_at=or_now(payload.resulted_at),
        resulted_by=staff.id,
    )
    # Saving the result and completing the order happen in one commit.
    order.status = "completed"
    db.add(result)
    commit_or_409(db)
    db.refresh(result)
    return result


# ---------------------------------------------------------------- vital signs


@router.get(
    "/vital-signs",
    response_model=List[VitalSignRead],
    dependencies=[Depends(get_current_staff)],
)
def list_vital_signs(visit_id: Optional[int] = None, db: Session = Depends(get_db)):
    return list_rows(db, models.VitalSign, visit_id=visit_id)


@router.get(
    "/vital-signs/{vital_sign_id}",
    response_model=VitalSignRead,
    dependencies=[Depends(get_current_staff)],
)
def get_vital_sign(vital_sign_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, models.VitalSign, vital_sign_id, "Vital sign")


@router.post(
    "/vital-signs",
    response_model=VitalSignRead,
    status_code=201,
)
def create_vital_sign(
    payload: VitalSignCreate,
    staff: models.Staff = Depends(require_roles("nurse", "doctor")),
    db: Session = Depends(get_db),
):
    visit = get_or_404(db, models.Visit, payload.visit_id, "Visit")
    require_in_progress(visit)
    data = payload.model_dump()
    if all(data[field] is None for field in MEASUREMENTS):
        raise HTTPException(status_code=400, detail="At least one measurement is required")
    data["recorded_at"] = or_now(payload.recorded_at)
    data["recorded_by"] = staff.id
    return create_row(db, models.VitalSign, data)


# ---------------------------------------------------------------- consumable usage


@router.get(
    "/consumable-usage",
    response_model=List[ConsumableUsageRead],
    dependencies=[Depends(get_current_staff)],
)
def list_consumable_usage(visit_id: Optional[int] = None, db: Session = Depends(get_db)):
    return list_rows(db, models.ConsumableUsage, visit_id=visit_id)


@router.get(
    "/consumable-usage/{usage_id}",
    response_model=ConsumableUsageRead,
    dependencies=[Depends(get_current_staff)],
)
def get_consumable_usage(usage_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, models.ConsumableUsage, usage_id, "Consumable usage")


@router.post(
    "/consumable-usage",
    response_model=ConsumableUsageRead,
    status_code=201,
)
def create_consumable_usage(
    payload: ConsumableUsageCreate,
    staff: models.Staff = Depends(require_roles("nurse", "doctor")),
    db: Session = Depends(get_db),
):
    visit = get_or_404(db, models.Visit, payload.visit_id, "Visit")
    get_or_404(db, models.Consumable, payload.consumable_id, "Consumable")
    require_in_progress(visit)
    if payload.procedure_history_id is not None:
        procedure = get_or_404(
            db, models.ProcedureHistory, payload.procedure_history_id, "Procedure history"
        )
        if procedure.visit_id != visit.id:
            raise HTTPException(
                status_code=400,
                detail=f"Procedure history {procedure.id} does not belong to visit {visit.id}",
            )
    data = payload.model_dump()
    data["used_at"] = or_now(payload.used_at)
    data["recorded_by"] = staff.id
    return create_row(db, models.ConsumableUsage, data)
