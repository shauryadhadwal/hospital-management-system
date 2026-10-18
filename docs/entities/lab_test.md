# lab_test

**Context:** ref (lookup)

## Purpose

Catalogue of lab tests (e.g. CBC, blood glucose, Troponin) carrying a standard price. Doctors pick from it when ordering a test, and billing draws the price from it.

## Decisions

- **Brought back as an entity, at the user's request (2026-10-19).** It was dropped earlier and `lab_order` held a free-text test name. Reason: lab charges need a price source, and a catalogue gives one consistent name and one price per test. Matches how `procedures` and `medication` work.
- **Plain price list: name and price only.** No reference range and no coding system. Reason: keeps the design basic. The earlier version also held a reference range; that is not restored.
- **Orders refer to it.** `lab_order.lab_test_id` replaces the free-text `test_name`.

## Columns

| Column | Type | Key / constraints | Notes |
|---|---|---|---|
| `id` | INT | PK | Auto-increment |
| `name` | VARCHAR(100) | NOT NULL, UNIQUE | e.g. CBC, Troponin |
| `price` | DECIMAL(10,2) | NOT NULL | Standard price |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set when the row is inserted |
| `updated_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set on insert and refreshed on every update |

## Constraints

Sanity-level checks, in addition to the keys and NOT NULLs in Columns. A NULL passes a CHECK, so optional columns are only checked when filled in.

- `ck_lab_test_price`: `price >= 0`
- `ck_lab_test_name_not_blank`: `TRIM(name) <> ''`

## Relationships

- lab_test 1 -> 0..n lab_order
