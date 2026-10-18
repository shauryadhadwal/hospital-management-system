# procedure_history

**Context:** clinical (centred on visit)

## Purpose

One row for each procedure carried out during a visit (e.g. an X-ray or an ECG). It refers to the `procedures` price list and records when it was done and by whom.

## Decisions

- **Kept as its own table.** Reason: it records what was done, while `procedures` is only the catalogue of what can be done. It is the record that a procedure charge on an invoice is based on, though invoice lines do not link to it.
- **Named `procedure_history`, formerly `performed_procedure`.** Reason: requested by the user.

## Columns

| Column | Type | Key / constraints | Notes |
|---|---|---|---|
| `id` | INT | PK | Auto-increment |
| `visit_id` | INT | FK -> visit, NOT NULL |  |
| `procedure_id` | INT | FK -> procedures, NOT NULL |  |
| `performed_at` | DATETIME | NOT NULL |  |
| `performed_by` | INT | FK -> doctor, NOT NULL | Doctor who did it |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set when the row is inserted |
| `updated_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set on insert and refreshed on every update |

## Constraints

Sanity-level checks, in addition to the keys and NOT NULLs in Columns. A NULL passes a CHECK, so optional columns are only checked when filled in.

No checks beyond the keys: both foreign keys and `performed_at` / `performed_by` are NOT NULL.

## Relationships

- visit 1 -> 0..n procedure_history
- procedures 1 -> 0..n procedure_history
- doctor 1 -> 0..n procedure_history (performed by)
- procedure_history 1 -> 0..n consumable_usage (optional)
