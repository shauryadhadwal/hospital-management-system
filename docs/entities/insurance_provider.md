# insurance_provider

**Context:** patient

## Purpose

Master list of insurers, e.g. a health insurance company or a government scheme. `insurance_policy` refers to it.

## Decisions

- **Kept as an entity.** Reason: many patients share the same insurer, so one list keeps the insurer's name and contact details in one place, and claims need a clear record of which insurer they go to.

## Columns

| Column | Type | Key / constraints | Notes |
|---|---|---|---|
| `id` | INT | PK | Auto-increment |
| `name` | VARCHAR(100) | NOT NULL, UNIQUE |  |
| `phone` | VARCHAR(20) |  |  |
| `email` | VARCHAR(100) |  |  |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set when the row is inserted |
| `updated_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set on insert and refreshed on every update |

## Constraints

Sanity-level checks, in addition to the keys and NOT NULLs in Columns. A NULL passes a CHECK, so optional columns are only checked when filled in.

- `ck_provider_name_not_blank`: `TRIM(name) <> ''`

## Relationships

- insurance_provider 1 -> 0..n insurance_policy
