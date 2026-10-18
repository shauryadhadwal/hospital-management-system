from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

VisitType = Literal["outpatient", "emergency", "inpatient"]
VisitStatus = Literal["booked", "in progress", "completed", "cancelled", "no-show"]
LabOrderStatus = Literal["ordered", "completed", "cancelled"]


class AtTime(BaseModel):
    """Optional time for check-in, discharge and transfer. Blank means now."""

    at: Optional[datetime] = None


# ---------------------------------------------------------------- visit


class VisitCreate(BaseModel):
    patient_id: int
    doctor_id: int
    department_id: int
    visit_type: VisitType
    planned_start: datetime
    chief_complaint: Optional[str] = Field(default=None, max_length=255)


class VisitUpdate(BaseModel):
    visit_type: Optional[VisitType] = None
    chief_complaint: Optional[str] = Field(default=None, max_length=255)
    notes: Optional[str] = None


class VisitRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    doctor_id: int
    department_id: int
    visit_type: VisitType
    status: VisitStatus
    planned_start: Optional[datetime]
    actual_start: Optional[datetime]
    actual_end: Optional[datetime]
    chief_complaint: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------- bed assignment


class BedAssignmentCreate(BaseModel):
    visit_id: int
    bed_id: int
    start_time: Optional[datetime] = None


class BedTransfer(AtTime):
    bed_id: int


class BedAssignmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    visit_id: int
    bed_id: int
    start_time: datetime
    end_time: Optional[datetime]
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------- diagnosis


class DiagnosisCreate(BaseModel):
    visit_id: int
    description: str = Field(max_length=255)
    is_primary: bool = False


class DiagnosisUpdate(BaseModel):
    description: Optional[str] = Field(default=None, max_length=255)
    is_primary: Optional[bool] = None


class DiagnosisRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    visit_id: int
    description: str
    is_primary: bool
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------- procedure history


class ProcedureHistoryCreate(BaseModel):
    visit_id: int
    procedure_id: int
    performed_at: Optional[datetime] = None


class ProcedureHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    visit_id: int
    procedure_id: int
    performed_at: datetime
    performed_by: int
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------- prescription


class PrescriptionCreate(BaseModel):
    visit_id: int
    medication_id: int
    dose: str = Field(max_length=50)
    frequency: str = Field(max_length=50)
    duration_days: int = Field(gt=0)
    quantity: int = Field(gt=0)


class PrescriptionUpdate(BaseModel):
    medication_id: Optional[int] = None
    dose: Optional[str] = Field(default=None, max_length=50)
    frequency: Optional[str] = Field(default=None, max_length=50)
    duration_days: Optional[int] = Field(default=None, gt=0)
    quantity: Optional[int] = Field(default=None, gt=0)


class PrescriptionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    visit_id: int
    medication_id: int
    dose: str
    frequency: str
    duration_days: int
    quantity: int
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------- consumable usage


class ConsumableUsageCreate(BaseModel):
    visit_id: int
    consumable_id: int
    quantity: int = Field(gt=0)
    used_at: Optional[datetime] = None
    procedure_history_id: Optional[int] = None


class ConsumableUsageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    visit_id: int
    consumable_id: int
    procedure_history_id: Optional[int]
    quantity: int
    used_at: datetime
    recorded_by: int
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------- lab order


class LabOrderCreate(BaseModel):
    visit_id: int
    lab_test_id: int
    ordered_at: Optional[datetime] = None


class LabOrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    visit_id: int
    lab_test_id: int
    ordered_at: datetime
    ordered_by: int
    status: LabOrderStatus
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------- lab result


class LabResultCreate(BaseModel):
    lab_order_id: int
    result_text: str
    resulted_at: Optional[datetime] = None


class LabResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lab_order_id: int
    result_text: str
    resulted_at: datetime
    resulted_by: int
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------- vital sign


class VitalSignCreate(BaseModel):
    visit_id: int
    recorded_at: Optional[datetime] = None
    temperature_c: Optional[Decimal] = Field(default=None, ge=25, le=45)
    pulse_bpm: Optional[int] = Field(default=None, ge=20, le=300)
    systolic_bp: Optional[int] = Field(default=None, ge=40, le=300)
    diastolic_bp: Optional[int] = Field(default=None, ge=20, le=200)
    respiratory_rate: Optional[int] = Field(default=None, ge=4, le=80)
    oxygen_saturation: Optional[int] = Field(default=None, ge=0, le=100)


class VitalSignRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    visit_id: int
    recorded_by: int
    recorded_at: datetime
    temperature_c: Optional[Decimal]
    pulse_bpm: Optional[int]
    systolic_bp: Optional[int]
    diastolic_bp: Optional[int]
    respiratory_rate: Optional[int]
    oxygen_saturation: Optional[int]
    created_at: datetime
    updated_at: datetime
