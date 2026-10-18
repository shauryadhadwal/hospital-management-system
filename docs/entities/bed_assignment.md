# bed_assignment

**Context:** clinical (centred on visit)

## Purpose

One stay in one bed during an inpatient visit: the visit, the bed, a start time and an end time. A patient who moves from one bed to another (e.g. ICU to a general ward) gets two rows. A blank end time means the patient is still in that bed.

## Decisions

- **Kept as its own table.** Reason: requested by the user. It is how bed occupancy is worked out (a bed is free if it has no row with a blank end time), which is why `bed` stores no status. It also records ward moves.
- **Not a single bed column on `visit`.** Reason: a transfer would overwrite the old bed and lose the history.
- **Bed charges are priced from the room.** The days of a stay are calendar dates touched, counted from `start_time` and `end_time` by the bed-day rule in `invoice_line` (minimum 1, the transfer date goes to the room moved into, the discharge date counts); the rate is `room.daily_rate` of the bed's room, copied onto an `invoice_line` when the invoice is made. That line points back to the stay (`invoice_line.source_type = 'bed_assignment'`, `source_id` = the stay), so each stay is billed once.

## Columns

| Column | Type | Key / constraints | Notes |
|---|---|---|---|
| `id` | INT | PK | Auto-increment |
| `visit_id` | INT | FK -> visit, NOT NULL |  |
| `bed_id` | INT | FK -> bed, NOT NULL |  |
| `start_time` | DATETIME | NOT NULL |  |
| `end_time` | DATETIME |  | Blank = patient is still in this bed |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set when the row is inserted |
| `updated_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set on insert and refreshed on every update |

A bed is free when it has no row with a blank `end_time`.

## Constraints

Sanity-level checks, in addition to the keys and NOT NULLs in Columns. A NULL passes a CHECK, so optional columns are only checked when filled in.

- `ck_bed_assignment_times`: `end_time IS NULL OR end_time > start_time`
- One open stay per bed: unique index on `bed_id` where `end_time IS NULL` (a bed cannot hold two patients at once)
- One open stay per visit: unique index on `visit_id` where `end_time IS NULL` (a patient is in one bed at a time)

The two open-stay rules are partial unique indexes: native in PostgreSQL; in MySQL use a generated column (e.g. `open_bed_id = IF(end_time IS NULL, bed_id, NULL)`) with a unique index on it.

Ordering rules the application enforces (a CHECK cannot see other tables; see `docs/entities.md`):
- Discharge closes the open stay first, then sets the visit to `completed`. A completed visit therefore has no open stay, so the bed is freed and the stay can be billed.
- On a transfer, the old stay is closed and the new one opened in the same action, with the new `start_time` equal to the old `end_time`.
- Stays are only added to inpatient visits (`visit_type = 'inpatient'`).

## Relationships

- visit 1 -> 0..n bed_assignment
- bed 1 -> 0..n bed_assignment
- bed_assignment 1 -> 0..1 invoice_line (by `source_type` / `source_id`)
