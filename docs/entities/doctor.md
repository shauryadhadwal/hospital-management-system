# doctor

**Context:** org (hospital structure and staff)

## Purpose

Doctor subtype of `staff`. Holds the fields that only doctors have: medical licence number, specialty, and consultation fee. Visits refer to it.

## Decisions

- **Kept as a separate subtype table of `staff`.** Reason: visits and consultation billing need a doctor, not just any staff member. Doctor-only fields would otherwise sit empty on every nurse and clerk row, and "must be a doctor" could not be enforced.
- **Specialty is a plain text column on `doctor`.** Reason: the `specialty` entity was dropped.

## Columns

| Column | Type | Key / constraints | Notes |
|---|---|---|---|
| `id` | INT | PK | Auto-increment |
| `staff_id` | INT | FK -> staff, NOT NULL, UNIQUE | UNIQUE gives the 0..1 doctor row per staff member; the staff member must have role = doctor |
| `license_number` | VARCHAR(50) | NOT NULL, UNIQUE | Medical licence number |
| `specialty` | VARCHAR(100) | NOT NULL | Free text |
| `consultation_fee` | DECIMAL(10,2) | NOT NULL |  |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set when the row is inserted |
| `updated_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set on insert and refreshed on every update |

Other tables that refer to a doctor (e.g. `visit.doctor_id`) point at `doctor.id`, not at `staff.id`.

## Constraints

Sanity-level checks, in addition to the keys and NOT NULLs in Columns. A NULL passes a CHECK, so optional columns are only checked when filled in.

- `ck_doctor_fee`: `consultation_fee >= 0`
- `ck_doctor_license_not_blank`: `TRIM(license_number) <> ''`
- `ck_doctor_specialty_not_blank`: `TRIM(specialty) <> ''`

## Relationships

- staff 1 -> 0..1 doctor
- doctor 1 -> 0..n visit
- doctor 1 -> 0..n lab_order (ordered by)
- doctor 1 -> 0..n procedure_history (performed by)
