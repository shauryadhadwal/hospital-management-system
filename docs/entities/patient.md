# patient

**Context:** patient

## Purpose

The person receiving care. Holds demographics (name, date of birth, sex), contact details and an emergency contact. Visits and insurance policies all refer to it.

## Decisions

- **Kept as an entity.** Reason: every clinical and billing record belongs to a patient; nothing else works without it.
- **No `age` column; only `date_of_birth` is stored.** Reason: age goes stale and cannot be computed in the database. The frontend collects age, and the backend derives `date_of_birth` from it before saving. Trade-off: a date derived from an age is an estimate, not the real birth date.
- **Derivation rule: `date_of_birth` = today minus the age in years.** Reason: the stored date is a real date and the age it implies is correct on the day of registration. Confirmed by the user.
- **Emergency contact is three columns on `patient`** (name, phone, relationship), not a separate table. Reason: keeps the design basic. Trade-off: one contact per patient.

## Columns

| Column | Type | Key / constraints | Notes |
|---|---|---|---|
| `id` | INT | PK | Auto-increment; also serves as the hospital patient number |
| `first_name` | VARCHAR(50) | NOT NULL |  |
| `last_name` | VARCHAR(50) | NOT NULL |  |
| `date_of_birth` | DATE | NOT NULL | Derived by the backend from the age entered in the frontend |
| `sex` | VARCHAR(10) | NOT NULL | male, female, other |
| `phone` | VARCHAR(20) | NOT NULL |  |
| `email` | VARCHAR(100) |  |  |
| `address` | VARCHAR(255) |  |  |
| `emergency_contact_name` | VARCHAR(100) |  |  |
| `emergency_contact_phone` | VARCHAR(20) |  |  |
| `emergency_contact_relationship` | VARCHAR(50) |  | e.g. spouse, parent |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set when the row is inserted |
| `updated_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set on insert and refreshed on every update |

## Constraints

Sanity-level checks, in addition to the keys and NOT NULLs in Columns. A NULL passes a CHECK, so optional columns are only checked when filled in.

- `ck_patient_sex`: `sex IN ('male', 'female', 'other')`
- `ck_patient_name_not_blank`: `TRIM(first_name) <> '' AND TRIM(last_name) <> ''`
- `ck_patient_phone_not_blank`: `TRIM(phone) <> ''`

"Date of birth is not in the future" is left to the application: CHECK constraints cannot use `CURRENT_DATE` in MySQL.

## Relationships

- patient 1 -> 0..n insurance_policy
- patient 1 -> 0..n visit
