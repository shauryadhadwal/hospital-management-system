# procedures

**Context:** ref (lookup)

## Purpose

Catalogue of procedures (e.g. X-ray, ECG, appendectomy) carrying a standard price. It is the price list that billing draws from.

## Decisions

- **Kept as an entity.** Reason: it is the source of price for billing, and it gives one consistent name per procedure.
- **Renamed from `procedure_code` to `procedures`.** Reason: requested by the user.
- **Plain price list: name and price only.** No standard coding system (no CPT/ICD-style codes). Reason: keeps the design basic.
- **Procedures performed on a visit are recorded in `procedure_history`** (formerly `performed_procedure`), one row per procedure performed, which refers to `procedures`. Reason: the catalogue holds what can be done; the history holds what was done.

## Columns

| Column | Type | Key / constraints | Notes |
|---|---|---|---|
| `id` | INT | PK | Auto-increment |
| `name` | VARCHAR(100) | NOT NULL, UNIQUE | e.g. X-ray, ECG |
| `price` | DECIMAL(10,2) | NOT NULL | Standard price |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set when the row is inserted |
| `updated_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set on insert and refreshed on every update |

## Constraints

Sanity-level checks, in addition to the keys and NOT NULLs in Columns. A NULL passes a CHECK, so optional columns are only checked when filled in.

- `ck_procedures_price`: `price >= 0`
- `ck_procedures_name_not_blank`: `TRIM(name) <> ''`

## Relationships

- procedures 1 -> 0..n procedure_history
