# prescription

**Context:** clinical (centred on visit)

## Purpose

One medication line prescribed during a visit: which medication, dose, frequency, duration and the quantity to dispense. A visit can have several.

## Decisions

- **Merged with the former `prescription_item` entity, so there is one table with one row per medication line.** Reason: a visit usually has one prescription and the prescriber is already the visit's doctor, so a separate header added little.
- **Trade-off: no record of "this set of lines is one prescription".** Rows are grouped by visit; two prescriptions in one visit simply appear as more lines. Reason: accepted to keep the design basic.
- **The prescriber is the visit's doctor; it is not stored separately.** Reason: the visit already identifies the doctor.
- **`quantity` is the number of units to dispense, entered by the doctor (added after the design review).** Reason: `dose` and `frequency` are free text, so a billable quantity cannot be worked out from them. The medication invoice line takes its quantity from this column and its unit price from `medication.price`. The prescription is still not linked to the invoice line (see `invoice_line`).

## Columns

| Column | Type | Key / constraints | Notes |
|---|---|---|---|
| `id` | INT | PK | Auto-increment |
| `visit_id` | INT | FK -> visit, NOT NULL |  |
| `medication_id` | INT | FK -> medication, NOT NULL |  |
| `dose` | VARCHAR(50) | NOT NULL | e.g. 1 tablet |
| `frequency` | VARCHAR(50) | NOT NULL | e.g. twice a day |
| `duration_days` | INT | NOT NULL | Must be > 0 |
| `quantity` | INT | NOT NULL | Units to dispense (in the medication's unit price terms); must be > 0 |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set when the row is inserted |
| `updated_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set on insert and refreshed on every update |

One row per medication line. The prescriber is the visit's doctor.

## Constraints

Sanity-level checks, in addition to the keys and NOT NULLs in Columns. A NULL passes a CHECK, so optional columns are only checked when filled in.

- `ck_prescription_duration`: `duration_days > 0`
- `ck_prescription_quantity`: `quantity > 0`
- `ck_prescription_text_not_blank`: `TRIM(dose) <> '' AND TRIM(frequency) <> ''`

## Relationships

- visit 1 -> 0..n prescription
- medication 1 -> 0..n prescription
