# lab_result

**Context:** clinical (centred on visit)

## Purpose

The result of a lab order. At most one result per order.

## Decisions

- **Kept as its own table, separate from `lab_order`.** Reason: the result arrives later than the order and has its own timing; a separate table also leaves room for fuller results later. Merging it into `lab_order` was considered and not chosen.
- **Records who entered the result (`resulted_by`, a staff reference; added after the design review).** Reason: the journey had a result arriving with nobody to enter it. The person is normally a lab technician (staff role `lab`).
- **Saving a result marks its order `completed`, in the same action.** See `lab_order`.

## Columns

| Column | Type | Key / constraints | Notes |
|---|---|---|---|
| `id` | INT | PK | Auto-increment |
| `lab_order_id` | INT | FK -> lab_order, NOT NULL, UNIQUE | UNIQUE gives the 0..1 result per order |
| `result_text` | TEXT | NOT NULL |  |
| `resulted_at` | DATETIME | NOT NULL |  |
| `resulted_by` | INT | FK -> staff, NOT NULL | Staff member who entered the result |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set when the row is inserted |
| `updated_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set on insert and refreshed on every update |

## Constraints

Sanity-level checks, in addition to the keys and NOT NULLs in Columns. A NULL passes a CHECK, so optional columns are only checked when filled in.

- `ck_lab_result_text_not_blank`: `TRIM(result_text) <> ''`

## Relationships

- lab_order 1 -> 0..1 lab_result
- staff 1 -> 0..n lab_result (resulted by)
