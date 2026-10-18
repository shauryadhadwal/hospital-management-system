# Hospital Administration

## Role
Runs the hospital's structure, people and prices, and oversees billing and insurance. Needs reliable master data and a clear view of money owed and paid.

## Daily jobs
- Manage departments, staff and doctors.
- Manage wards, rooms and beds.
- Maintain the price lists for procedures, medication, lab tests and consumables, and room rates.
- Oversee invoices, payments and insurance claims.

## Covered by
- `department`, `staff`, `doctor`
- `ward`, `room`, `bed`
- `procedures`, `medication`, `lab_test` and `consumable` (price lists)
- `room` (type and daily rate)
- `invoice`, `invoice_line`, `payment`, `insurance_claim`

## Gaps
- Procedure and medication lines have no link to `procedure_history` or `prescription`, so double billing (or omission) there is not prevented. Bed-stay, lab and consumable lines are linked and billed once.
- The claim amount is typed by hand; the policy holds no coverage terms.
- Login and roles now live on `staff` (username, hashed password, role). Sign-in history and password resets are not stored.

