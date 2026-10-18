# bed

**Context:** org (hospital structure and staff)

## Purpose

A single bed inside a room (e.g. Bed 2). It is what a patient is assigned to during an inpatient stay, via `bed_assignment`.

## Decisions

- **Kept as an entity.** Reason: bed occupancy is the core inpatient fact (which beds are free, who is in which bed), and ward and room need something to point at.
- **Bed status (free, occupied, under maintenance) is not stored.** Occupancy is worked out from `bed_assignment`. Reason: avoids a stored value that can go out of step with the assignments.

## Columns

| Column | Type | Key / constraints | Notes |
|---|---|---|---|
| `id` | INT | PK | Auto-increment |
| `room_id` | INT | FK -> room, NOT NULL |  |
| `bed_number` | VARCHAR(20) | NOT NULL | Label within the room, e.g. 2 |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set when the row is inserted |
| `updated_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set on insert and refreshed on every update |

`(room_id, bed_number)` is unique. No status column: occupancy comes from `bed_assignment`.

## Constraints

Sanity-level checks, in addition to the keys and NOT NULLs in Columns. A NULL passes a CHECK, so optional columns are only checked when filled in.

- `ck_bed_number_not_blank`: `TRIM(bed_number) <> ''`

## Relationships

- room 1 -> 0..n bed
- bed 1 -> 0..n bed_assignment
