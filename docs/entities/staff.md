# staff

**Context:** org (hospital structure and staff)

## Purpose

All employees in one table, holding the shared HR fields (name, contact, role, department, hire date) and the login details (username, hashed password, whether login is allowed). `doctor` is a subtype built on top of it.

## Decisions

- **Kept as an entity.** Reason: doctors, nurses, receptionists, lab technicians and administrators all need name, contact and department; one table gives visits and invoices a single place to point at "who did this".
- **Staff is the supertype; doctor is the subtype.** Doctor-only fields live on `doctor`. Reason: keeps shared fields in one place without putting doctor-only fields on every employee. Nurse and other-role subtype tables are out of scope for now.
- **Login lives on `staff`; there is no separate `user_account` entity.** Fields: username, hashed password (never the plain password), and a flag for whether the person may log in. Reason: the design is one login per staff member, and `staff` already holds the role (doctor, receptionist, nurse, lab, admin), so a separate table would only repeat a one-to-one link. Login and logout events are not stored.
- **Roles are doctor, receptionist, nurse, lab and admin (`lab` added after the design review).** Reason: lab results need someone to enter them. There is no billing-clerk role: the receptionist raises invoices, claims and payments, and admin oversees them. Collecting lab samples is not recorded.
- **Trade-off accepted:** password hashes sit next to HR data, so queries and exports of `staff` must leave them out, and staff who never log in carry empty login columns. If sign-in history, password resets or two-factor codes are added later, the login can be split into its own entity.

## Columns

| Column | Type | Key / constraints | Notes |
|---|---|---|---|
| `id` | INT | PK | Auto-increment |
| `department_id` | INT | FK -> department, NOT NULL |  |
| `first_name` | VARCHAR(50) | NOT NULL |  |
| `last_name` | VARCHAR(50) | NOT NULL |  |
| `role` | VARCHAR(20) | NOT NULL | doctor, receptionist, nurse, lab, admin |
| `phone` | VARCHAR(20) |  |  |
| `email` | VARCHAR(100) | UNIQUE |  |
| `hire_date` | DATE | NOT NULL |  |
| `username` | VARCHAR(50) | UNIQUE | Blank for staff who never log in |
| `password_hash` | VARCHAR(255) |  | Hash only, never the plain password; leave out of queries and exports |
| `login_enabled` | BOOLEAN | NOT NULL, DEFAULT false | Whether the person may log in |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set when the row is inserted |
| `updated_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Set on insert and refreshed on every update |

## Constraints

Sanity-level checks, in addition to the keys and NOT NULLs in Columns. A NULL passes a CHECK, so optional columns are only checked when filled in.

- `ck_staff_role`: `role IN ('doctor', 'receptionist', 'nurse', 'lab', 'admin')`
- `ck_staff_name_not_blank`: `TRIM(first_name) <> '' AND TRIM(last_name) <> ''`
- `ck_staff_login_complete`: `login_enabled = false OR (username IS NOT NULL AND password_hash IS NOT NULL)` (nobody can be allowed to log in without a username and password)

## Relationships

- department 1 -> 0..n staff
- staff 1 -> 0..1 doctor
- staff 1 -> 0..n vital_sign (recorded by)
- staff 1 -> 0..n consumable_usage (recorded by)
- staff 1 -> 0..n lab_result (resulted by)
