# ward

**Context:** org (hospital structure and staff)

## Purpose

A ward inside a department (e.g. General Ward A, ICU). It is the top of the inpatient location chain: ward -> room -> bed.

## Decisions

- **Kept as an entity.** Reason: inpatient care needs to say where a patient is; the ward is the level nurses and bed management work at, and it ties locations back to a department.

## Columns

| Column | Type | Key / constraints | Notes |
|---|---|---|---|
| `id` | INT | PK | Auto-increment |
| `department_id` | INT | FK -> department, NOT NULL |  |
| `name` | VARCHAR(100) | NOT NULL | e.g. General Ward A, ICU |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set when the row is inserted |
| `updated_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set on insert and refreshed on every update |

`(department_id, name)` is unique.

## Constraints

Sanity-level checks, in addition to the keys and NOT NULLs in Columns. A NULL passes a CHECK, so optional columns are only checked when filled in.

- `ck_ward_name_not_blank`: `TRIM(name) <> ''`

## Relationships

- department 1 -> 0..n ward
- ward 1 -> 0..n room
