# consumable

**Context:** ref (lookup)

## Purpose

Catalogue of single-use supplies (e.g. bandage, syringe, suture, gloves, IV set) carrying a unit price. Staff pick from it when recording what was used on a visit.

## Decisions

- **Kept as an entity, separate from `medication`.** Reason: requested by the user. Drugs are prescribed and dosed; supplies are used up in care. Keeping them apart avoids a misleading `medication` row like "bandage".
- **Simple name, unit and price list. No stock levels.** Reason: pharmacy and store stock is out of scope for the basic design. Matches how `medication` works.

## Columns

| Column | Type | Key / constraints | Notes |
|---|---|---|---|
| `id` | INT | PK | Auto-increment |
| `name` | VARCHAR(100) | NOT NULL, UNIQUE | e.g. Crepe bandage 10 cm |
| `unit` | VARCHAR(30) | NOT NULL | e.g. piece, pack, pair |
| `price` | DECIMAL(10,2) | NOT NULL | Price per unit |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set when the row is inserted |
| `updated_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set on insert and refreshed on every update |

No stock columns.

## Constraints

Sanity-level checks, in addition to the keys and NOT NULLs in Columns. A NULL passes a CHECK, so optional columns are only checked when filled in.

- `ck_consumable_price`: `price >= 0`
- `ck_consumable_text_not_blank`: `TRIM(name) <> '' AND TRIM(unit) <> ''`

## Relationships

- consumable 1 -> 0..n consumable_usage
