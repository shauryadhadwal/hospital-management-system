# department

**Context:** org (hospital structure and staff)

## Purpose

The hospital's departments, clinical and administrative (e.g. Cardiology, Emergency, Radiology, Billing).

## Decisions

- **Kept as an entity.** Reason: it is the main organizing unit; staff, ward and visit all hang off it. With `specialty` dropped, it is also how doctors are grouped for booking.
- **Name only; no clinical/administrative flag.** Reason: keeps the design basic.

## Columns

| Column | Type | Key / constraints | Notes |
|---|---|---|---|
| `id` | INT | PK | Auto-increment |
| `name` | VARCHAR(100) | NOT NULL, UNIQUE | e.g. Cardiology, Billing |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set when the row is inserted |
| `updated_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set on insert and refreshed on every update |

## Constraints

Sanity-level checks, in addition to the keys and NOT NULLs in Columns. A NULL passes a CHECK, so optional columns are only checked when filled in.

- `ck_department_name_not_blank`: `TRIM(name) <> ''`

## Relationships

- department 1 -> 0..n staff
- department 1 -> 0..n ward
- department 1 -> 0..n visit (department hosting the visit)
