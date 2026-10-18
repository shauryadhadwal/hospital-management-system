from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    false,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )


# ---------------------------------------------------------------- ref


class Procedure(TimestampMixin, Base):
    __tablename__ = "procedures"
    __table_args__ = (
        CheckConstraint("price >= 0", name="ck_procedures_price"),
        CheckConstraint("TRIM(name) <> ''", name="ck_procedures_name_not_blank"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)


class Medication(TimestampMixin, Base):
    __tablename__ = "medication"
    __table_args__ = (
        UniqueConstraint("name", "form", "strength", name="uq_medication_name_form_strength"),
        CheckConstraint("price >= 0", name="ck_medication_price"),
        CheckConstraint(
            "TRIM(name) <> '' AND TRIM(form) <> '' AND TRIM(strength) <> ''",
            name="ck_medication_name_not_blank",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    form: Mapped[str] = mapped_column(String(30), nullable=False)
    strength: Mapped[str] = mapped_column(String(30), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)


class LabTest(TimestampMixin, Base):
    __tablename__ = "lab_test"
    __table_args__ = (
        CheckConstraint("price >= 0", name="ck_lab_test_price"),
        CheckConstraint("TRIM(name) <> ''", name="ck_lab_test_name_not_blank"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)


class Consumable(TimestampMixin, Base):
    __tablename__ = "consumable"
    __table_args__ = (
        CheckConstraint("price >= 0", name="ck_consumable_price"),
        CheckConstraint("TRIM(name) <> '' AND TRIM(unit) <> ''", name="ck_consumable_text_not_blank"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    unit: Mapped[str] = mapped_column(String(30), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)


# ---------------------------------------------------------------- org


class Department(TimestampMixin, Base):
    __tablename__ = "department"
    __table_args__ = (
        CheckConstraint("TRIM(name) <> ''", name="ck_department_name_not_blank"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)


class Staff(TimestampMixin, Base):
    __tablename__ = "staff"
    __table_args__ = (
        CheckConstraint(
            "role IN ('doctor', 'receptionist', 'nurse', 'lab', 'admin')",
            name="ck_staff_role",
        ),
        CheckConstraint(
            "TRIM(first_name) <> '' AND TRIM(last_name) <> ''",
            name="ck_staff_name_not_blank",
        ),
        CheckConstraint(
            "login_enabled = false OR (username IS NOT NULL AND password_hash IS NOT NULL)",
            name="ck_staff_login_complete",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    department_id: Mapped[int] = mapped_column(ForeignKey("department.id"), nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    email: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    hire_date: Mapped[date] = mapped_column(Date, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(50), unique=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255))
    login_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=false()
    )


class Doctor(TimestampMixin, Base):
    __tablename__ = "doctor"
    __table_args__ = (
        CheckConstraint("consultation_fee >= 0", name="ck_doctor_fee"),
        CheckConstraint("TRIM(license_number) <> ''", name="ck_doctor_license_not_blank"),
        CheckConstraint("TRIM(specialty) <> ''", name="ck_doctor_specialty_not_blank"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    staff_id: Mapped[int] = mapped_column(ForeignKey("staff.id"), nullable=False, unique=True)
    license_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    specialty: Mapped[str] = mapped_column(String(100), nullable=False)
    consultation_fee: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    staff: Mapped["Staff"] = relationship()


class Ward(TimestampMixin, Base):
    __tablename__ = "ward"
    __table_args__ = (
        UniqueConstraint("department_id", "name", name="uq_ward_department_name"),
        CheckConstraint("TRIM(name) <> ''", name="ck_ward_name_not_blank"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    department_id: Mapped[int] = mapped_column(ForeignKey("department.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)


class Room(TimestampMixin, Base):
    __tablename__ = "room"
    __table_args__ = (
        UniqueConstraint("ward_id", "room_number", name="uq_room_ward_number"),
        CheckConstraint("TRIM(room_number) <> ''", name="ck_room_number_not_blank"),
        CheckConstraint("room_type IN ('private', 'shared')", name="ck_room_type"),
        CheckConstraint("daily_rate >= 0", name="ck_room_daily_rate"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ward_id: Mapped[int] = mapped_column(ForeignKey("ward.id"), nullable=False)
    room_number: Mapped[str] = mapped_column(String(20), nullable=False)
    room_type: Mapped[str] = mapped_column(String(20), nullable=False)
    daily_rate: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    ward: Mapped["Ward"] = relationship()


class Bed(TimestampMixin, Base):
    __tablename__ = "bed"
    __table_args__ = (
        UniqueConstraint("room_id", "bed_number", name="uq_bed_room_number"),
        CheckConstraint("TRIM(bed_number) <> ''", name="ck_bed_number_not_blank"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("room.id"), nullable=False)
    bed_number: Mapped[str] = mapped_column(String(20), nullable=False)

    room: Mapped["Room"] = relationship()


# ---------------------------------------------------------------- patient


class Patient(TimestampMixin, Base):
    __tablename__ = "patient"
    __table_args__ = (
        CheckConstraint("sex IN ('male', 'female', 'other')", name="ck_patient_sex"),
        CheckConstraint(
            "TRIM(first_name) <> '' AND TRIM(last_name) <> ''",
            name="ck_patient_name_not_blank",
        ),
        CheckConstraint("TRIM(phone) <> ''", name="ck_patient_phone_not_blank"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    sex: Mapped[str] = mapped_column(String(10), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(100))
    address: Mapped[Optional[str]] = mapped_column(String(255))
    emergency_contact_name: Mapped[Optional[str]] = mapped_column(String(100))
    emergency_contact_phone: Mapped[Optional[str]] = mapped_column(String(20))
    emergency_contact_relationship: Mapped[Optional[str]] = mapped_column(String(50))


class InsuranceProvider(TimestampMixin, Base):
    __tablename__ = "insurance_provider"
    __table_args__ = (
        CheckConstraint("TRIM(name) <> ''", name="ck_provider_name_not_blank"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    email: Mapped[Optional[str]] = mapped_column(String(100))


class InsurancePolicy(TimestampMixin, Base):
    __tablename__ = "insurance_policy"
    __table_args__ = (
        UniqueConstraint("provider_id", "policy_number", name="uq_policy_provider_number"),
        CheckConstraint("valid_to >= valid_from", name="ck_policy_validity"),
        CheckConstraint("TRIM(policy_number) <> ''", name="ck_policy_number_not_blank"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patient.id"), nullable=False)
    provider_id: Mapped[int] = mapped_column(ForeignKey("insurance_provider.id"), nullable=False)
    policy_number: Mapped[str] = mapped_column(String(50), nullable=False)
    valid_from: Mapped[date] = mapped_column(Date, nullable=False)
    valid_to: Mapped[date] = mapped_column(Date, nullable=False)


# ---------------------------------------------------------------- clinical


class Visit(TimestampMixin, Base):
    __tablename__ = "visit"
    __table_args__ = (
        CheckConstraint(
            "visit_type IN ('outpatient', 'emergency', 'inpatient')",
            name="ck_visit_type",
        ),
        CheckConstraint(
            "status IN ('booked', 'in progress', 'completed', 'cancelled', 'no-show')",
            name="ck_visit_status",
        ),
        CheckConstraint(
            "actual_end IS NULL OR (actual_start IS NOT NULL AND actual_end >= actual_start)",
            name="ck_visit_times_order",
        ),
        CheckConstraint(
            "(status = 'booked' AND planned_start IS NOT NULL AND actual_start IS NULL) "
            "OR (status = 'in progress' AND actual_start IS NOT NULL AND actual_end IS NULL) "
            "OR (status = 'completed' AND actual_start IS NOT NULL AND actual_end IS NOT NULL) "
            "OR (status IN ('cancelled', 'no-show') AND actual_start IS NULL)",
            name="ck_visit_status_times",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patient.id"), nullable=False)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctor.id"), nullable=False)
    department_id: Mapped[int] = mapped_column(ForeignKey("department.id"), nullable=False)
    visit_type: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    planned_start: Mapped[Optional[datetime]] = mapped_column(DateTime)
    actual_start: Mapped[Optional[datetime]] = mapped_column(DateTime)
    actual_end: Mapped[Optional[datetime]] = mapped_column(DateTime)
    chief_complaint: Mapped[Optional[str]] = mapped_column(String(255))
    notes: Mapped[Optional[str]] = mapped_column(Text)


class BedAssignment(TimestampMixin, Base):
    __tablename__ = "bed_assignment"
    __table_args__ = (
        CheckConstraint(
            "end_time IS NULL OR end_time > start_time",
            name="ck_bed_assignment_times",
        ),
        Index("uq_open_stay_bed", "bed_id", unique=True, sqlite_where=text("end_time IS NULL")),
        Index("uq_open_stay_visit", "visit_id", unique=True, sqlite_where=text("end_time IS NULL")),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    visit_id: Mapped[int] = mapped_column(ForeignKey("visit.id"), nullable=False)
    bed_id: Mapped[int] = mapped_column(ForeignKey("bed.id"), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime)


class Diagnosis(TimestampMixin, Base):
    __tablename__ = "diagnosis"
    __table_args__ = (
        CheckConstraint("TRIM(description) <> ''", name="ck_diagnosis_description_not_blank"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    visit_id: Mapped[int] = mapped_column(ForeignKey("visit.id"), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    is_primary: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=false()
    )


class ProcedureHistory(TimestampMixin, Base):
    __tablename__ = "procedure_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    visit_id: Mapped[int] = mapped_column(ForeignKey("visit.id"), nullable=False)
    procedure_id: Mapped[int] = mapped_column(ForeignKey("procedures.id"), nullable=False)
    performed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    performed_by: Mapped[int] = mapped_column(ForeignKey("doctor.id"), nullable=False)


class Prescription(TimestampMixin, Base):
    __tablename__ = "prescription"
    __table_args__ = (
        CheckConstraint("duration_days > 0", name="ck_prescription_duration"),
        CheckConstraint("quantity > 0", name="ck_prescription_quantity"),
        CheckConstraint(
            "TRIM(dose) <> '' AND TRIM(frequency) <> ''",
            name="ck_prescription_text_not_blank",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    visit_id: Mapped[int] = mapped_column(ForeignKey("visit.id"), nullable=False)
    medication_id: Mapped[int] = mapped_column(ForeignKey("medication.id"), nullable=False)
    dose: Mapped[str] = mapped_column(String(50), nullable=False)
    frequency: Mapped[str] = mapped_column(String(50), nullable=False)
    duration_days: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)


class ConsumableUsage(TimestampMixin, Base):
    __tablename__ = "consumable_usage"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_consumable_usage_quantity"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    visit_id: Mapped[int] = mapped_column(ForeignKey("visit.id"), nullable=False)
    consumable_id: Mapped[int] = mapped_column(ForeignKey("consumable.id"), nullable=False)
    procedure_history_id: Mapped[Optional[int]] = mapped_column(ForeignKey("procedure_history.id"))
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    used_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    recorded_by: Mapped[int] = mapped_column(ForeignKey("staff.id"), nullable=False)


class LabOrder(TimestampMixin, Base):
    __tablename__ = "lab_order"
    __table_args__ = (
        CheckConstraint(
            "status IN ('ordered', 'completed', 'cancelled')",
            name="ck_lab_order_status",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    visit_id: Mapped[int] = mapped_column(ForeignKey("visit.id"), nullable=False)
    lab_test_id: Mapped[int] = mapped_column(ForeignKey("lab_test.id"), nullable=False)
    ordered_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ordered_by: Mapped[int] = mapped_column(ForeignKey("doctor.id"), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="ordered", server_default="ordered"
    )

    lab_test: Mapped["LabTest"] = relationship()
    result: Mapped[Optional["LabResult"]] = relationship(uselist=False)


class LabResult(TimestampMixin, Base):
    __tablename__ = "lab_result"
    __table_args__ = (
        CheckConstraint("TRIM(result_text) <> ''", name="ck_lab_result_text_not_blank"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lab_order_id: Mapped[int] = mapped_column(
        ForeignKey("lab_order.id"), nullable=False, unique=True
    )
    result_text: Mapped[str] = mapped_column(Text, nullable=False)
    resulted_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    resulted_by: Mapped[int] = mapped_column(ForeignKey("staff.id"), nullable=False)


class VitalSign(TimestampMixin, Base):
    __tablename__ = "vital_sign"
    __table_args__ = (
        CheckConstraint("temperature_c BETWEEN 25.0 AND 45.0", name="ck_vital_temperature"),
        CheckConstraint("pulse_bpm BETWEEN 20 AND 300", name="ck_vital_pulse"),
        CheckConstraint("systolic_bp BETWEEN 40 AND 300", name="ck_vital_systolic"),
        CheckConstraint("diastolic_bp BETWEEN 20 AND 200", name="ck_vital_diastolic"),
        CheckConstraint(
            "systolic_bp IS NULL OR diastolic_bp IS NULL OR systolic_bp > diastolic_bp",
            name="ck_vital_bp_order",
        ),
        CheckConstraint("respiratory_rate BETWEEN 4 AND 80", name="ck_vital_respiratory"),
        CheckConstraint("oxygen_saturation BETWEEN 0 AND 100", name="ck_vital_spo2"),
        CheckConstraint(
            "COALESCE(temperature_c, pulse_bpm, systolic_bp, diastolic_bp, "
            "respiratory_rate, oxygen_saturation) IS NOT NULL",
            name="ck_vital_not_empty",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    visit_id: Mapped[int] = mapped_column(ForeignKey("visit.id"), nullable=False)
    recorded_by: Mapped[int] = mapped_column(ForeignKey("staff.id"), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    temperature_c: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 1))
    pulse_bpm: Mapped[Optional[int]] = mapped_column(Integer)
    systolic_bp: Mapped[Optional[int]] = mapped_column(Integer)
    diastolic_bp: Mapped[Optional[int]] = mapped_column(Integer)
    respiratory_rate: Mapped[Optional[int]] = mapped_column(Integer)
    oxygen_saturation: Mapped[Optional[int]] = mapped_column(Integer)


# ---------------------------------------------------------------- billing


class Invoice(TimestampMixin, Base):
    __tablename__ = "invoice"
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft', 'issued', 'paid', 'cancelled')",
            name="ck_invoice_status",
        ),
        CheckConstraint("TRIM(invoice_number) <> ''", name="ck_invoice_number_not_blank"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    visit_id: Mapped[int] = mapped_column(ForeignKey("visit.id"), nullable=False, unique=True)
    invoice_number: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    invoice_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="draft", server_default="draft"
    )


class InvoiceLine(TimestampMixin, Base):
    __tablename__ = "invoice_line"
    __table_args__ = (
        UniqueConstraint("source_type", "source_id", name="uq_invoice_line_source"),
        CheckConstraint("quantity > 0", name="ck_invoice_line_quantity"),
        CheckConstraint("unit_price >= 0", name="ck_invoice_line_unit_price"),
        CheckConstraint("TRIM(description) <> ''", name="ck_invoice_line_description_not_blank"),
        CheckConstraint(
            "source_type IN ('bed_assignment', 'lab_order', 'consumable_usage')",
            name="ck_invoice_line_source_type",
        ),
        CheckConstraint(
            "(source_type IS NULL) = (source_id IS NULL)",
            name="ck_invoice_line_source_pair",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoice.id"), nullable=False)
    source_type: Mapped[Optional[str]] = mapped_column(String(30))
    source_id: Mapped[Optional[int]] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)


class Payment(TimestampMixin, Base):
    __tablename__ = "payment"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_payment_amount"),
        CheckConstraint(
            "method IN ('cash', 'card', 'UPI', 'bank transfer')",
            name="ck_payment_method",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoice.id"), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    paid_at: Mapped[date] = mapped_column(Date, nullable=False)
    method: Mapped[str] = mapped_column(String(20), nullable=False)
    reference: Mapped[Optional[str]] = mapped_column(String(50))


class InsuranceClaim(TimestampMixin, Base):
    __tablename__ = "insurance_claim"
    __table_args__ = (
        CheckConstraint("amount_claimed > 0", name="ck_claim_amount"),
        CheckConstraint(
            "status IN ('submitted', 'approved', 'rejected', 'paid')",
            name="ck_claim_status",
        ),
        CheckConstraint(
            "(approved_date IS NULL OR approved_date >= submitted_date) AND "
            "(paid_date IS NULL OR (approved_date IS NOT NULL AND paid_date >= approved_date))",
            name="ck_claim_dates",
        ),
        CheckConstraint(
            "(status NOT IN ('approved', 'paid') OR approved_date IS NOT NULL) AND "
            "(status <> 'paid' OR paid_date IS NOT NULL)",
            name="ck_claim_status_dates",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoice.id"), nullable=False)
    policy_id: Mapped[int] = mapped_column(ForeignKey("insurance_policy.id"), nullable=False)
    amount_claimed: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="submitted", server_default="submitted"
    )
    submitted_date: Mapped[date] = mapped_column(Date, nullable=False)
    approved_date: Mapped[Optional[date]] = mapped_column(Date)
    paid_date: Mapped[Optional[date]] = mapped_column(Date)
