# Doctor

## Role
Sees patients and records what was found and done. Needs the day's visits, the patient's history and the tools to prescribe and order tests.

## Daily jobs
- See today's visits and open a patient's history.
- Record diagnoses.
- Prescribe medication.
- Record procedures carried out.
- Order lab tests and read the results.
- Review vitals taken during a visit or stay.

## Covered by
- `visit` (the day's list and history)
- `diagnosis`
- `prescription` and `medication`
- `procedure_history` and `procedures`
- `lab_order`, `lab_test` and `lab_result`
- `vital_sign`

## Gaps
- No allergy record (`allergy` was dropped), so there is no safety check before prescribing.
- Consultation notes and chief complaint are columns on `visit` (settled).
- Prescriptions carry a quantity to dispense, which the doctor enters.

## Questions to discuss
- Accept the missing allergy record, or restore allergies as free text on `patient`?
