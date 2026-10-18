# medication

**Context:** ref (lookup)

## Purpose

Drug catalogue (name, form, strength) carrying a unit price. Doctors pick from it when prescribing, and billing draws the price from it.

## Decisions

- **Kept as an entity.** Reason: doctors pick from a list instead of typing drug names, which avoids spelling variants and gives one place for the price. Matches how `procedures` works.
- **Simple name, strength and price list. No stock levels.** Reason: pharmacy stock is out of scope for the basic design.

## Columns

| Column | Type | Key / constraints | Notes |
|---|---|---|---|
| `id` | INT | PK | Auto-increment |
| `name` | VARCHAR(100) | NOT NULL |  |
| `form` | VARCHAR(30) | NOT NULL | e.g. tablet, syrup, injection |
| `strength` | VARCHAR(30) | NOT NULL | e.g. 500 mg |
| `price` | DECIMAL(10,2) | NOT NULL | Unit price |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set when the row is inserted |
| `updated_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set on insert and refreshed on every update |

`(name, form, strength)` is unique. No stock columns.

## Constraints

Sanity-level checks, in addition to the keys and NOT NULLs in Columns. A NULL passes a CHECK, so optional columns are only checked when filled in.

- `ck_medication_price`: `price >= 0`
- `ck_medication_name_not_blank`: `TRIM(name) <> '' AND TRIM(form) <> '' AND TRIM(strength) <> ''`

## Relationships

- medication 1 -> 0..n prescription
