# Brainstorming — dropped entities

Entities considered and dropped during the entity review. Kept here so they can be revisited as their own design question if needs change.

| Entity | Context | What it was | Why dropped | Replaced by |
|---|---|---|---|---|
| specialty | ref | Lookup of medical specialties (cardiology, ortho, ...) | Dropped at the user's request; overlaps with `department` | Plain text `specialty` column on `doctor` |
| diagnosis_code | ref | ICD-style diagnosis catalogue | Dropped at the user's request; no coded diagnoses needed for the basic design | `diagnosis` holds free text |
| lab_test | ref | Lab test catalogue with price and reference range | Dropped at the user's request, then **restored (2026-10-19)** without the reference range, so lab charges have a price source | Back as `lab_test`; `lab_order` refers to it |
| doctor_schedule | org | Recurring weekly availability slots per doctor | Dropped at the user's request | None; availability is handled outside the system |
| appointment | clinical | Booked slot: patient, doctor, planned time, status | Merged into `visit` at the user's request: a booking and the care that follows are one record | `visit`, with a status (booked, in progress, completed, cancelled, no-show) and planned and actual times |
| prescription_item | clinical | Medication lines (dose, frequency, duration) under a prescription header | Merged into `prescription` at the user's request: a visit usually has one prescription and the prescriber is the visit's doctor, so the header added little | `prescription`, where each row is one medication line |
| allergy | patient | Known allergies per patient, one row each | Dropped at the user's request | None; allergies are not recorded in the system |

## Open follow-ups caused by these drops

- **Lab pricing:** resolved by restoring `lab_test` as a price list (2026-10-19).
- **Claims and coded diagnoses:** if insurance claims later need coded diagnoses, `diagnosis_code` comes back as a design question.
- **Allergies:** nothing records them now. If prescribing safety checks are wanted later, `allergy` comes back as a design question (free text, or linked to `medication`).
- **Login:** a separate `user_account` entity was considered and not added; login details are columns on `staff`. It comes back as a design question if sign-in history, password resets or two-factor codes are wanted.
- **Consumable billing:** resolved after the design review; `consumable_usage` is a billable `source_type` on `invoice_line`.
- **Lab technician and billing roles:** a `lab` role was added to `staff` so lab results have an author. A separate billing-clerk role was considered and not added; the receptionist raises invoices, claims and payments.
- **Coverage terms and approved amounts:** the policy holds no coverage percentage and the claim has no separate approved amount; the claim amount is typed by hand. They come back as a design question if partial approvals or co-pay rules are wanted.
- **Shared (family) policies:** one policy row belongs to one patient; a shared policy number is not supported.
- **Leave and holidays** were never in scope for `doctor_schedule`; they would be a separate design question if scheduling returns.
