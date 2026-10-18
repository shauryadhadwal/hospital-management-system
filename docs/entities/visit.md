# visit

**Context:** clinical (centred on visit)

## Purpose

The hub of the clinical and billing records. One visit, from booking to being seen: outpatient, emergency or inpatient. It records the patient, the doctor, the department, a type, a status and planned and actual times. Diagnoses, procedures, prescriptions, consumables used, lab orders, vitals, bed stays and the invoice all hang off it.

## Decisions

- **Kept as the hub, as one table with a type column (outpatient / emergency / inpatient).** Reason: keeps the design small, rather than separate tables per kind of care.
- **Named `visit`, renamed from `encounter`.** Reason: requested by the user. The plain wording fits a booking, a walk-in and an inpatient stay alike.
- **Merged with the former `appointment` entity.** Reason: requested by the user. A status column is simpler than a second table at this design size.
  - A booked visit is created with status `booked` and moves to `in progress` on arrival.
  - A walk-in or emergency is created directly as `in progress`.
  - Status values: `booked`, `in progress`, `completed`, `cancelled`, `no-show`.
  - `cancelled` and `no-show` visits stay as rows and never get clinical records.
- **Bookings are not checked against doctor availability.** Reason: `doctor_schedule` was dropped, so a booking only records what was booked.
- **An inpatient stay and an outpatient visit share the same table.** A blank actual end time means the patient is still admitted.
- **Consequences to keep in mind:**
  - Reports that count visits must filter by status.
  - The type and status columns must stay consistent with each other.
- **Discharge order (application rule):** the open `bed_assignment` is closed first, then the visit is set to `completed` with `actual_end`. An invoice is created only for a `completed` visit.

## Columns

| Column | Type | Key / constraints | Notes |
|---|---|---|---|
| `id` | INT | PK | Auto-increment |
| `patient_id` | INT | FK -> patient, NOT NULL |  |
| `doctor_id` | INT | FK -> doctor, NOT NULL | The attending doctor; also the prescriber |
| `department_id` | INT | FK -> department, NOT NULL | Department hosting the visit |
| `visit_type` | VARCHAR(20) | NOT NULL | outpatient, emergency, inpatient |
| `status` | VARCHAR(20) | NOT NULL | booked, in progress, completed, cancelled, no-show |
| `planned_start` | DATETIME |  | Blank for walk-ins and emergencies |
| `actual_start` | DATETIME |  | Blank until the patient arrives |
| `actual_end` | DATETIME |  | Blank while still in progress or admitted |
| `chief_complaint` | VARCHAR(255) |  | Why the patient came |
| `notes` | TEXT |  | Consultation notes |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set when the row is inserted |
| `updated_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set on insert and refreshed on every update |

Chief complaint and notes are on `visit`, which settles open question 1 in `docs/entities.md`.

## Constraints

Sanity-level checks, in addition to the keys and NOT NULLs in Columns. A NULL passes a CHECK, so optional columns are only checked when filled in.

- `ck_visit_type`: `visit_type IN ('outpatient', 'emergency', 'inpatient')`
- `ck_visit_status`: `status IN ('booked', 'in progress', 'completed', 'cancelled', 'no-show')`
- `ck_visit_times_order`: `actual_end IS NULL OR (actual_start IS NOT NULL AND actual_end >= actual_start)`
- `ck_visit_status_times`, which keeps status and times consistent:
  - `booked`: `planned_start IS NOT NULL AND actual_start IS NULL`
  - `in progress`: `actual_start IS NOT NULL AND actual_end IS NULL`
  - `completed`: `actual_start IS NOT NULL AND actual_end IS NOT NULL`
  - `cancelled`, `no-show`: `actual_start IS NULL`

  Written as one CHECK:
  `(status = 'booked' AND planned_start IS NOT NULL AND actual_start IS NULL) OR (status = 'in progress' AND actual_start IS NOT NULL AND actual_end IS NULL) OR (status = 'completed' AND actual_start IS NOT NULL AND actual_end IS NOT NULL) OR (status IN ('cancelled', 'no-show') AND actual_start IS NULL)`

## Relationships

- patient 1 -> 0..n visit
- doctor 1 -> 0..n visit
- department 1 -> 0..n visit
- visit 1 -> 0..n bed_assignment, diagnosis, procedure_history, prescription, consumable_usage, lab_order, vital_sign
- visit 1 -> 0..1 invoice
