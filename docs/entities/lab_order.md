# lab_order

**Context:** clinical (centred on visit)

## Purpose

A lab test ordered during a visit, e.g. a blood glucose or a CBC. The test is picked from the `lab_test` catalogue, which also supplies its price. The outcome is held by `lab_result`.

## Decisions

- **Kept as its own table.** Reason: ordering a test and receiving its result are separate steps with different timing. Requested by the user.
- **Test is chosen from the `lab_test` catalogue, not typed as free text.** Reason: the catalogue was brought back (2026-10-19) so lab charges have a price source and test names stay consistent. `lab_test_id` replaces the old `test_name` column.
- **`lab_result` stays a separate table, not merged into `lab_order`.** Reason: merging was considered and not chosen.
- **No price column on the order.** The price is read from `lab_test` when the invoice is made and copied to `invoice_line.unit_price`. The line points back to the order (`invoice_line.source_type = 'lab_order'`, `source_id` = the order), so each order is billed once. Reason: one price per test, kept in one place.
- **`completed` is set by the application when the `lab_result` is saved.** Reason: it is a stored copy of a derived fact (the order has a result), so it is never set by hand or separately from saving the result.

## Columns

| Column | Type | Key / constraints | Notes |
|---|---|---|---|
| `id` | INT | PK | Auto-increment |
| `visit_id` | INT | FK -> visit, NOT NULL |  |
| `lab_test_id` | INT | FK -> lab_test, NOT NULL | The test ordered, e.g. CBC |
| `ordered_at` | DATETIME | NOT NULL |  |
| `ordered_by` | INT | FK -> doctor, NOT NULL | Ordering doctor |
| `status` | VARCHAR(20) | NOT NULL, DEFAULT 'ordered' | ordered, completed, cancelled |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set when the row is inserted |
| `updated_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set on insert and refreshed on every update |

No price column: the price comes from `lab_test`.

## Constraints

Sanity-level checks, in addition to the keys and NOT NULLs in Columns. A NULL passes a CHECK, so optional columns are only checked when filled in.

- `ck_lab_order_status`: `status IN ('ordered', 'completed', 'cancelled')`

## Relationships

- visit 1 -> 0..n lab_order
- lab_test 1 -> 0..n lab_order
- lab_order 1 -> 0..1 lab_result
- lab_order 1 -> 0..1 invoice_line (by `source_type` / `source_id`)
