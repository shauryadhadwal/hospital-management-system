# payment

**Context:** billing

## Purpose

A payment made against an invoice: the amount, the date and the method (cash, card, UPI, bank transfer). An invoice can have several, e.g. a deposit followed by the balance.

## Decisions

- **Kept as its own table.** Reason: taking money is part of billing; without it you cannot say what has been paid or what is outstanding. A separate table handles part payments and refunds, which a single "paid" flag on the invoice cannot.
- **Amount paid and balance are derived, not stored.** The amount paid on an invoice is the sum of its payments (the patient's own money). The balance is the invoice total minus the insurer's share (the sum of the invoice's `insurance_claim` rows with status `paid`) minus that sum. Reason: avoids two sources of truth that can drift apart, and the insurer's payout is tracked on the claim, not as a `payment` row.
- **`payment` is only for money from the patient.** Reason: insurer payouts have their own life on `insurance_claim` (see that entity), so `method` has no insurance value.
- **Method is one of: cash, card, UPI, bank transfer.** Reason: these are the payment methods the hospital accepts.
- **`reference` holds the transaction id for non-cash payments (added after the design review).** Reason: a UPI, card or bank payment has an id that is needed to match it against the bank statement. Optional, since cash has none.
- **`paid_at` stays a date, not a datetime.** Reason: the bill only needs the day; deliberate, not an oversight.
- **Payment rules the application enforces:** the invoice is `issued`, and the amount does not exceed the current balance. Recording the payment that brings the balance to zero also sets the invoice to `paid`.

## Columns

| Column | Type | Key / constraints | Notes |
|---|---|---|---|
| `id` | INT | PK | Auto-increment |
| `invoice_id` | INT | FK -> invoice, NOT NULL |  |
| `amount` | DECIMAL(10,2) | NOT NULL | Must be > 0 |
| `paid_at` | DATE | NOT NULL |  |
| `method` | VARCHAR(20) | NOT NULL | cash, card, UPI, bank transfer |
| `reference` | VARCHAR(50) |  | Transaction id (e.g. UPI reference); blank for cash |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set when the row is inserted |
| `updated_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set on insert and refreshed on every update |

## Constraints

Sanity-level checks, in addition to the keys and NOT NULLs in Columns. A NULL passes a CHECK, so optional columns are only checked when filled in.

- `ck_payment_amount`: `amount > 0`
- `ck_payment_method`: `method IN ('cash', 'card', 'UPI', 'bank transfer')`

## Relationships

- invoice 1 -> 0..n payment
