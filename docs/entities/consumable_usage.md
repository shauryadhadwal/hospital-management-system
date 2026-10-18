# consumable_usage

**Context:** clinical (centred on visit)

## Purpose

One row for each consumable used during a visit, with the quantity, the time and the staff member who recorded it. When the item was used in a procedure (e.g. sutures in an operation), the row can point at that `procedure_history` row.

## Decisions

- **Kept as its own table.** Reason: requested by the user. `consumable` is the catalogue of what exists; this records what was used, as `procedures` and `procedure_history` do.
- **Linked to the visit, with an optional link to a procedure.** Reason: bedside use (a dressing on the ward, a syringe in the emergency room) belongs to no procedure, while operation supplies should be traceable to one.
- **Records the staff member who used or recorded it (staff reference).** Reason: mostly nurses, so each use can be traced, as with `vital_sign`.
- **Billed automatically, once, through `invoice_line` (decided after the design review).** The invoice line points back to the usage row (`invoice_line.source_type = 'consumable_usage'`, `source_id` = the usage), with quantity = this row's `quantity` and unit price copied from `consumable.price`. Reason: a consumable use is easy to forget on a hand-typed bill; linking it means it cannot be missed or billed twice. This differs from `procedure_history` and `prescription`, which stay unlinked.

## Columns

| Column | Type | Key / constraints | Notes |
|---|---|---|---|
| `id` | INT | PK | Auto-increment |
| `visit_id` | INT | FK -> visit, NOT NULL |  |
| `consumable_id` | INT | FK -> consumable, NOT NULL |  |
| `procedure_history_id` | INT | FK -> procedure_history | Blank when not used in a procedure |
| `quantity` | INT | NOT NULL | Must be > 0 |
| `used_at` | DATETIME | NOT NULL |  |
| `recorded_by` | INT | FK -> staff, NOT NULL | Staff member who used or recorded it |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set when the row is inserted |
| `updated_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set on insert and refreshed on every update |

## Constraints

Sanity-level checks, in addition to the keys and NOT NULLs in Columns. A NULL passes a CHECK, so optional columns are only checked when filled in.

- `ck_consumable_usage_quantity`: `quantity > 0`
- A CHECK cannot see other tables, so the application enforces that a given `procedure_history_id` belongs to the same visit.

## Relationships

- visit 1 -> 0..n consumable_usage
- consumable 1 -> 0..n consumable_usage
- procedure_history 1 -> 0..n consumable_usage (optional)
- staff 1 -> 0..n consumable_usage (recorded by)
- consumable_usage 1 -> 0..1 invoice_line (by `source_type` / `source_id`, not a foreign key)
