# invoice_line

**Context:** billing

## Purpose

One itemised charge on an invoice, such as a consultation fee, an X-ray or a drug. It holds a description, a quantity and a unit price. The line total is quantity times unit price. A bed-stay, lab or consumable line records its source as a type and an id (`bed_assignment`, `lab_order` or `consumable_usage`).

## Decisions

- **Kept as its own table.** Reason: an invoice's total is worked out from its lines, so `invoice`, `payment` and `insurance_claim` do not work without it. Requested by the user.
- **Polymorphic source: `source_type` + `source_id`, at the user's request (2026-10-19).** Replaces the two nullable foreign keys (`bed_assignment_id`, `lab_order_id`) added earlier the same day. Reason: one pair of columns can point at any kind of source record, so a new billable source is a new allowed `source_type` value rather than a new column. Allowed types for now: `bed_assignment`, `lab_order` and `consumable_usage` (the last added after the design review, which settled the former open question on consumable billing).
- **Trade-off: the database cannot enforce the link.** `source_id` is not a real foreign key, because one column cannot reference two tables. The application must check that the source row exists, and a deleted source can leave a dangling id. Reason accepted: the user chose this flexibility over database-enforced links.
- **No trace links to `procedure_history` or `prescription`, or for the consultation fee.** Those lines carry only description, quantity and unit price, copied from the price list when the invoice is made. Reason: keeps the design basic; they can be added later if double billing becomes a problem there too.
- **Each source can be billed once.** `(source_type, source_id)` is UNIQUE, so a stay, test or consumable use appears on at most one line. A line has at most one source.
- **Bed-stay line:** quantity = bed days of the stay, unit price = `room.daily_rate` of the bed's room. A stay still open (blank `end_time`) is billed once it ends.
  - **Bed-day rule:** bed days are the calendar dates the stay touches, i.e. `date(end_time) − date(start_time) + 1`, minus 1 when the stay ended in a transfer (the transfer date is billed to the room the patient moved into), with a minimum of 1. The discharge date counts. Example: ICU from day 1, transfer on day 2, discharge on day 3 gives ICU 1 day and General Ward A 2 days.
  - **Known edge, accepted:** a stay entered and transferred out on the same date bills 1 day, so that date can appear in two rooms.
- **Lab line:** quantity 1, unit price = `lab_test.price`.
- **Consumable line:** quantity = `consumable_usage.quantity`, unit price = `consumable.price`.
- **Medication line:** quantity = `prescription.quantity`, unit price = `medication.price`. It carries no source link (see above).
- **Unit price is copied onto the line.** Reason: a later price-list change must not alter an old bill.

## Columns

| Column | Type | Key / constraints | Notes |
|---|---|---|---|
| `id` | INT | PK | Auto-increment |
| `invoice_id` | INT | FK -> invoice, NOT NULL |  |
| `source_type` | VARCHAR(30) |  | `bed_assignment`, `lab_order` or `consumable_usage`; blank on lines with no source |
| `source_id` | INT |  | id of the row in the table named by `source_type`; no FK (see Decisions) |
| `description` | VARCHAR(255) | NOT NULL |  |
| `quantity` | INT | NOT NULL | Must be > 0 |
| `unit_price` | DECIMAL(10,2) | NOT NULL | Copied from the price list when the invoice is made |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set when the row is inserted |
| `updated_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set on insert and refreshed on every update |

Line total = `quantity` x `unit_price` (derived, not stored).

## Constraints

Sanity-level checks, in addition to the keys and NOT NULLs in Columns. A NULL passes a CHECK, so optional columns are only checked when filled in.

- `ck_invoice_line_quantity`: `quantity > 0`
- `ck_invoice_line_unit_price`: `unit_price >= 0`
- `ck_invoice_line_description_not_blank`: `TRIM(description) <> ''`
- `ck_invoice_line_source_type`: `source_type IN ('bed_assignment', 'lab_order', 'consumable_usage')`
- `ck_invoice_line_source_pair`: `(source_type IS NULL) = (source_id IS NULL)` (both filled or both blank)
- Unique index on `(source_type, source_id)`; NULLs do not clash, so lines without a source are unaffected.
- A CHECK cannot see other tables, so the application enforces that the source row exists and belongs to the same visit as the invoice when it adds the line.

## Relationships

- invoice 1 -> 0..n invoice_line
- bed_assignment 1 -> 0..1 invoice_line (by `source_type` / `source_id`, not a foreign key)
- lab_order 1 -> 0..1 invoice_line (same)
- consumable_usage 1 -> 0..1 invoice_line (same)
