# Receptionist

## Role
Front desk. Registers patients, books and checks in visits, admits patients to beds and takes payment. Needs to find a patient and start a visit quickly.

## Daily jobs
- Register a new patient and look up an existing one.
- Book a visit with a doctor, and check the patient in on arrival.
- Admit an inpatient to a bed.
- Take payment against an invoice.
- Capture the patient's insurance details.

## Covered by
- `patient` (registration, lookup)
- `visit` (booking and check-in through its status)
- `invoice` and `invoice_line` (raising the bill; there is no separate billing-clerk role)
- `insurance_claim` (typing the claim amount and submitting it)
- `payment` (with the transaction reference for non-cash payments)
- `bed_assignment` (admitting to a bed)
- `insurance_policy` and `insurance_provider`

## Gaps
- No free-slot view: `doctor_schedule` was dropped, so bookings only record what was booked and are not checked against availability.
- The hospital patient number is `patient.id` (settled); lookup is by name or phone, and nothing prevents duplicate registrations.

## Questions to discuss
- Restore a simple weekly doctor schedule, or accept bookings that only record what was booked?
