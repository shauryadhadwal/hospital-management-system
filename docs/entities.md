# Hospital Management System — Entities

Status: **final, confirmed by the user (2026-10-19); `lab_test` re-added and room type and rate added the same day; `consumable` and `consumable_usage` added the same day at the user's request; amended after the adversarial design review (billing rules, ordering rules, `lab` role, extra columns), see the entity docs.** This lists which entities exist: 26 entities, each with a doc in `docs/entities/`. Dropped and merged entities are in `docs/brainstorming.md`; persona coverage is in `docs/personas/`. Columns and detailed relationships come next, in separate docs.

## Entities (26, in 5 bounded contexts)

### ref — lookups
| Entity | Purpose |
|---|---|
| procedures | Procedure catalogue; carries standard price |
| medication | Drug catalogue; carries unit price |
| lab_test | Lab test catalogue; carries standard price |
| consumable | Single-use supplies catalogue (bandages, syringes, sutures); carries unit price, no stock |

### org — hospital structure and staff
| Entity | Purpose |
|---|---|
| department | Clinical and administrative departments |
| staff | All employees (shared HR fields, role: doctor / receptionist / nurse / lab / admin, login: username + hashed password) |
| doctor | Doctor subtype of staff: licence, specialty, consultation fee |
| ward | Ward within a department |
| room | Room within a ward; private or shared, with a daily rate |
| bed | Bed within a room |

### patient
| Entity | Purpose |
|---|---|
| patient | Demographics, contact, emergency contact |
| insurance_provider | Insurer master |
| insurance_policy | Patient's policy with an insurer, validity range |

### clinical — centred on **visit**
| Entity | Purpose |
|---|---|
| visit | **Hub.** One visit, from booking to being seen (outpatient / emergency / inpatient). Has a status (booked, in progress, completed, cancelled, no-show) and planned and actual times. Replaces the separate `appointment` entity |
| bed_assignment | Bed stays within an inpatient visit |
| diagnosis | Free-text diagnoses recorded on a visit |
| procedure_history | Procedures carried out in a visit (one row per procedure performed, refers to `procedures`) |
| prescription | One medication line prescribed in a visit (medication, dose, frequency, duration, quantity to dispense). Replaces the separate `prescription_item` entity |
| consumable_usage | Consumables used in a visit: item, quantity, time, who recorded it; optionally tied to a procedure_history row |
| lab_order | Lab test (from the `lab_test` catalogue) ordered in a visit |
| lab_result | Result for a lab order (0..1 per order), with the staff member who entered it |
| vital_sign | Vitals measured during a visit |

### billing
| Entity | Purpose |
|---|---|
| invoice | One per visit |
| invoice_line | Itemised charges: description, quantity, unit price. Bed-stay, lab and consumable lines name their source by `source_type` + `source_id` (`bed_assignment` / `lab_order` / `consumable_usage`, each billed once); consultation, procedure and medication lines have no source |
| payment | Payments against an invoice (patient's money only), with an optional transaction reference |
| insurance_claim | Claim against a policy for an invoice; typed amount, submitted / approved / paid dates |

## Key relationships
- department → staff, ward; staff → doctor (1:0..1); ward → room → bed
- patient → insurance_policy, visit; insurance_provider → insurance_policy
- visit → bed_assignment, diagnosis, procedure_history, prescription, consumable_usage, lab_order, vital_sign, invoice
- consumable → consumable_usage; procedure_history → consumable_usage (optional); staff → consumable_usage (recorded by)
- lab_test → lab_order → lab_result (0..1); staff → lab_result (resulted by)
- invoice → invoice_line, payment, insurance_claim; bed_assignment, lab_order, consumable_usage → invoice_line (0..1 each, via `source_type` / `source_id`); insurance_policy → insurance_claim

## Ordering rules (happy path)
The database cannot check these across tables, so the application enforces them. They are stated here once; the entity docs refer to them.
1. **Discharge:** close the open `bed_assignment` first, then set the visit to `completed` with `actual_end`.
2. **Invoice:** created only for a `completed` visit, as `draft`; set to `issued` once all lines are added.
3. **Claim:** created only on an `issued` invoice, for a policy that belongs to the visit's patient and was valid on the visit date; `amount_claimed` does not exceed the invoice total.
4. **Payment:** recorded only on an `issued` invoice; the amount cannot exceed the current balance.
5. **Stored statuses that mirror a derived fact are set with the fact:** `lab_order.status = 'completed'` when the `lab_result` is saved; `invoice.status = 'paid'` when a payment or paid claim brings the balance to zero.
6. **Bed days** on an invoice follow the bed-day rule in `docs/entities/invoice_line.md` (calendar dates touched, minimum 1).

## Out of scope (keeping the design basic)
**Happy path only, for now (2026-10-19).** The design covers the normal flow of a visit. Exception flows (rejected claims and resubmissions, cancelled and no-show visits, emergency visits, refunds) are not designed yet; the statuses that allow for them stay in the columns but are not worked through. Any can be raised later as its own design question.

Sign-in history, password resets and other auth extras (basic login is on `staff`), pharmacy stock and purchasing, operating-theatre scheduling, nurse/other staff subtype tables, audit trail, document/image storage, discharge summaries (use visit fields). Any can be raised later as its own design question.

## Decided in the column step
1. Consultation notes and chief complaint are columns on `visit`.
2. The hospital patient number is `patient.id`; the emergency contact is three columns on `patient`.
3. Consumables are billed automatically: `consumable_usage` is an allowed `source_type` on `invoice_line` (after the design review).

## Open design questions
1. Doctor availability (no weekly schedule, so no free-slot view) and allergies (no record, so no safety check before prescribing): accepted gaps, can be reopened.
2. Whether to record medication actually given by nurses, not just prescribed. Until decided, drugs given during an inpatient stay are not recorded or billed; only the prescription is.
