# diagnosis

**Context:** clinical (centred on visit)

## Purpose

A diagnosis recorded on a visit, as free text (e.g. "Type 2 diabetes"). A visit can have several; each row can say whether it is primary or secondary.

## Decisions

- **Kept as its own table.** Reason: recording what the doctor concluded is a core part of the medical record. A separate table lets a visit have more than one diagnosis, and lets one be added or corrected without editing the visit.
- **Free text only; no `diagnosis_code` catalogue.** Reason: the catalogue was dropped to keep the design basic.

## Columns

| Column | Type | Key / constraints | Notes |
|---|---|---|---|
| `id` | INT | PK | Auto-increment |
| `visit_id` | INT | FK -> visit, NOT NULL |  |
| `description` | VARCHAR(255) | NOT NULL | Free text |
| `is_primary` | BOOLEAN | NOT NULL, DEFAULT false | true = primary, false = secondary |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set when the row is inserted |
| `updated_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set on insert and refreshed on every update |

## Constraints

Sanity-level checks, in addition to the keys and NOT NULLs in Columns. A NULL passes a CHECK, so optional columns are only checked when filled in.

- `ck_diagnosis_description_not_blank`: `TRIM(description) <> ''`

## Relationships

- visit 1 -> 0..n diagnosis
