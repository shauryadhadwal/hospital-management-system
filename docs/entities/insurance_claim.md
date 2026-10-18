# insurance_claim

**Context:** billing

## Purpose

A claim sent to an insurer for an invoice, under a patient's policy. It holds the invoice, the policy, the amount claimed, a status (submitted, approved, rejected, paid) and dates. An invoice can have more than one claim, e.g. a resubmission after a rejection.

## Decisions

- **Kept as its own table.** Reason: it is the reason `insurance_provider` and `insurance_policy` exist. A claim has its own life (submitted, approved or rejected, then paid), separate from the invoice and from the patient's own payments.
- **Not folded into `payment`** (an insurance payment with method "insurance"). Reason: that would lose pending and rejected claims.
- **A claim with status `paid` counts toward the invoice.** The insurer's share of an invoice is the sum of its `paid` claims, and it reduces what the patient owes (balance = total − paid claims − payments). Reason: the insurer's payout is not a `payment` row, so the claim is where it is recorded.
- **Happy path:** one claim per invoice, going submitted → approved → paid. Rejection and resubmission are not designed yet.
- **`amount_claimed` is entered by hand by the receptionist who does the billing, and is the figure the balance uses (decided after the design review).** There are no coverage terms (percentage, limit, co-pay) on `insurance_policy`, and no separate approved amount: on the happy path the insurer pays what was claimed. The patient's share is therefore the invoice total minus the paid claim, known once the claim is `paid`.
- **`approved_date` and `paid_date` record when the insurer approved and paid.** Reason: `submitted_date` alone left no trace of when the insurer's money arrived.
- **Claim rules the application enforces** (a CHECK cannot see other tables): the invoice is `issued`; the policy belongs to the visit's patient; the policy's validity covers the visit date; `amount_claimed` does not exceed the invoice total.

## Columns

| Column | Type | Key / constraints | Notes |
|---|---|---|---|
| `id` | INT | PK | Auto-increment |
| `invoice_id` | INT | FK -> invoice, NOT NULL |  |
| `policy_id` | INT | FK -> insurance_policy, NOT NULL |  |
| `amount_claimed` | DECIMAL(10,2) | NOT NULL | Must be > 0 |
| `status` | VARCHAR(20) | NOT NULL, DEFAULT 'submitted' | submitted, approved, rejected, paid |
| `submitted_date` | DATE | NOT NULL |  |
| `approved_date` | DATE |  | Blank until the insurer approves |
| `paid_date` | DATE |  | Blank until the insurer pays |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set when the row is inserted |
| `updated_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set on insert and refreshed on every update |

## Constraints

Sanity-level checks, in addition to the keys and NOT NULLs in Columns. A NULL passes a CHECK, so optional columns are only checked when filled in.

- `ck_claim_amount`: `amount_claimed > 0`
- `ck_claim_status`: `status IN ('submitted', 'approved', 'rejected', 'paid')`
- `ck_claim_dates`: `(approved_date IS NULL OR approved_date >= submitted_date) AND (paid_date IS NULL OR (approved_date IS NOT NULL AND paid_date >= approved_date))`
- `ck_claim_status_dates`: `(status NOT IN ('approved', 'paid') OR approved_date IS NOT NULL) AND (status <> 'paid' OR paid_date IS NOT NULL)`

## Relationships

- invoice 1 -> 0..n insurance_claim
- insurance_policy 1 -> 0..n insurance_claim
