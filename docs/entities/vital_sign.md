# vital_sign

**Context:** clinical (centred on visit)

## Purpose

A set of measurements taken during a visit (temperature, pulse, blood pressure, respiratory rate, oxygen saturation), with the time they were taken. A visit can have many sets, e.g. every few hours for an inpatient.

## Decisions

- **Kept as its own table.** Reason: requested by the user. Vitals are part of nearly every clinical visit and are recorded repeatedly with a time. A separate table holds that history; fields on `visit` would hold only one set.
- **Common measurements are fixed fields, not free text.** Reason: consistent, comparable readings over time.
- **Records the staff member who took the set (staff reference).** Reason: mainly for nurses, so each set can be traced to who measured it.

## Columns

| Column | Type | Key / constraints | Notes |
|---|---|---|---|
| `id` | INT | PK | Auto-increment |
| `visit_id` | INT | FK -> visit, NOT NULL |  |
| `recorded_by` | INT | FK -> staff, NOT NULL | Staff member who took the set |
| `recorded_at` | DATETIME | NOT NULL |  |
| `temperature_c` | DECIMAL(4,1) |  | Degrees Celsius |
| `pulse_bpm` | INT |  | Beats per minute |
| `systolic_bp` | INT |  | mmHg |
| `diastolic_bp` | INT |  | mmHg |
| `respiratory_rate` | INT |  | Breaths per minute |
| `oxygen_saturation` | INT |  | SpO2 percent |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set when the row is inserted |
| `updated_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set on insert and refreshed on every update |

Each measurement is optional, since a set may not include every reading.

## Constraints

Sanity-level checks, in addition to the keys and NOT NULLs in Columns. A NULL passes a CHECK, so optional columns are only checked when filled in.

Ranges are wide on purpose: they reject typos and unit mix-ups (e.g. 986 for 98.6), not unusual patients.

- `ck_vital_temperature`: `temperature_c BETWEEN 25.0 AND 45.0`
- `ck_vital_pulse`: `pulse_bpm BETWEEN 20 AND 300`
- `ck_vital_systolic`: `systolic_bp BETWEEN 40 AND 300`
- `ck_vital_diastolic`: `diastolic_bp BETWEEN 20 AND 200`
- `ck_vital_bp_order`: `systolic_bp IS NULL OR diastolic_bp IS NULL OR systolic_bp > diastolic_bp`
- `ck_vital_respiratory`: `respiratory_rate BETWEEN 4 AND 80`
- `ck_vital_spo2`: `oxygen_saturation BETWEEN 0 AND 100`
- `ck_vital_not_empty`: `COALESCE(temperature_c, pulse_bpm, systolic_bp, diastolic_bp, respiratory_rate, oxygen_saturation) IS NOT NULL` (a set must contain at least one reading)

## Relationships

- visit 1 -> 0..n vital_sign
- staff 1 -> 0..n vital_sign (recorded by)
