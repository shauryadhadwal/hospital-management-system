# Nurse

## Role
Ward and bedside care. Takes vitals, manages beds and ward moves, collects samples and gives medication. Today the design gives nurses very little to work with.

## Daily jobs
- Record vitals during a visit or stay.
- Manage bed use and ward moves.
- Collect lab samples.
- Give medication as prescribed.

## Covered by
- `ward`, `room` and `bed` (the structure)
- `bed_assignment` (who is in which bed, and ward moves)
- `vital_sign` (with the staff member who recorded it)
- `consumable` and `consumable_usage` (supplies such as bandages and syringes used on a visit, with who recorded them)

## Gaps
- Vitals and consumable use record who took them (`recorded_by`). Nothing records who collected a lab sample; that is out of scope.
- No medication-administration record (giving doses); currently out of scope.
- Nurse subtype tables are out of scope; nurses are `staff` rows only.

## Questions to discuss
- Is recording medication given (not just prescribed) wanted at all?
