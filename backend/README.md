# Hospital Management System — Backend

FastAPI + SQLAlchemy + SQLite backend for the hospital design in `../docs/`. It has basic CRUD for all 26 entities and role-based login, so Peehu's journey (`../docs/user_journey.md`) can be carried out by each persona: admin, receptionist, nurse, doctor and lab technician. Happy path only.

## Requirements

- Python 3.9 or later (the code avoids 3.10-only syntax)
- No database server: SQLite is a single file, `hospital.db`, created on first run

## Setup

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Seed the database

Load the sample data from the repo's `data/` folder (one CSV per entity), then add the admin login:

```bash
.venv/bin/python seed_csv.py   # loads ../data/ ; every staff login has password: password
.venv/bin/python seed.py       # adds the admin login: admin / admin123
```

`data/` holds a hospital that has already run: 4 departments, 8 staff, wards, rooms and beds, the price lists, an insurer, 4 patients with their visits, vitals, lab work, bed stays, invoices, claims and payments.

**Logins.** After running the two seed commands above, these logins work:

| Name | Role | Username | Password |
|---|---|---|---|
| Admin User | admin | `admin` | `admin123` |
| Arvind Rao | doctor | `dr.rao` | `password` |
| Neha Iyer | doctor | `dr.iyer` | `password` |
| Anita Menon | nurse | `nurse.anita` | `password` |
| Vikram Singh | nurse | `nurse.vikram` | `password` |
| Meera Kapoor | receptionist | `reception.meera` | `password` |
| Ravi Kumar | lab | `lab.ravi` | `password` |
| Pooja Desai | lab | `lab.pooja` | `password` |

The staff passwords are stored in `data/staff.csv` as bcrypt hashes of `password`, which the backend accepts. To give every staff member a different password, run `seed_csv.py --password <pw>`: it replaces the hash for every staff member with a username, so they all log in with `<pw>`. The admin in `data/` (Sanjay Gupta) has no login, which is why `seed.py` adds `admin / admin123` (it also adds an `Administration` department).

Other ways to run it:

```bash
.venv/bin/python seed_csv.py --password pw   # every staff login gets password pw
.venv/bin/python seed_csv.py path/to/folder   # load your own folder instead of ../data/
.venv/bin/python seed.py                      # admin login only, on an empty database
```

**CSV format** (for editing `data/` or making your own folder)

- One file per table, named after the table: `department.csv`, `staff.csv`, `procedures.csv`, `bed_assignment.csv`, and so on. Any of the 26 tables can be loaded, and missing files are skipped. Files are loaded in foreign-key order, so a department always exists before its staff.
- The first row is the header, holding column names from `../docs/entities/<table>.md`. `created_at` and `updated_at` are optional: if a cell is filled in it is kept, if empty the current time is used.
- Give each row an `id` so other files can refer to it (e.g. `ward.csv` has `department_id=4`). If you leave `id` out, the database assigns one.
- Values: dates as `2026-10-20`, date-times as `2026-10-20 09:00:00` or `2026-10-20T09:00:00`, booleans as `true`/`false`, money as `1500.00`. An empty cell means "no value", so the column default applies (e.g. `status`).
- Passwords: `staff.csv` takes either `password_hash` (bcrypt or the backend's own format) or a plain `password` column, which is hashed before saving. `patient.csv` can take `age` instead of `date_of_birth`, converted the same way as the API does it.
- Running it again is safe: rows whose `id` already exists are skipped.
- On a bad value, an unknown column or a database error (e.g. a duplicate name or a missing foreign key), it stops and names the file, row and problem. The file that failed is not saved; files loaded before it are kept.

The script writes straight to the database and does **not** go through the API, so the ordering rules (e.g. "an invoice only for a completed visit") are not checked. Keep CSV data consistent with them.

### Start over

Stop the server, delete `hospital.db`, and run the seed commands again.

## Run the server

```bash
.venv/bin/uvicorn app.main:app --reload
```

- API: http://127.0.0.1:8000
- Interactive docs (Swagger): http://127.0.0.1:8000/docs

To try requests in Swagger, click **Authorize**, enter a staff username and password (e.g. `admin` / `admin123`), and every request after that is sent as that person. Log out and authorize again to switch persona.

## Run the tests

```bash
.venv/bin/pytest -q
```

`tests/test_journey.py` walks Peehu's whole journey through the API, logging in as each persona: the admin sets up the hospital, then come registration, check-in, vitals, the lab test, the ECG, admission, the ward transfer, discharge, the invoice, the insurance claim and the final UPI payment. It also checks that the wrong role is refused. The tests use their own `test_hospital.db`, which is deleted afterwards.

## Configuration

Environment variables, all optional:

| Variable | Default | Purpose |
|---|---|---|
| `HOSPITAL_DB_URL` | `sqlite:///./hospital.db` | Database URL |
| `HOSPITAL_SECRET_KEY` | `dev-secret-change-me` | Key used to sign login tokens |

To start from an empty database, see [Start over](#start-over).

## Logging in from code

```bash
# get a token (form data, not JSON)
curl -X POST http://127.0.0.1:8000/auth/login -d 'username=admin&password=admin123'
# use it
curl http://127.0.0.1:8000/auth/me -H 'Authorization: Bearer <access_token>'
```

Tokens last 8 hours. Only staff with `login_enabled = true`, a username and a password can log in.

## Who can do what

Any logged-in staff member can read. Writes are limited by role:

| Role | Can write |
|---|---|
| admin | departments, staff, doctors, wards, rooms, beds, procedures, medications, lab tests, consumables, insurance providers |
| receptionist | patients, insurance policies, visits (book, check in), bed assignments (admit, transfer), invoices, invoice lines, insurance claims, payments |
| nurse | visit check-in, vital signs, consumable usage, bed assignments (admit, transfer) |
| doctor | visit notes, chief complaint and type, discharge, diagnoses, procedure history, prescriptions, lab orders |
| lab | lab results |

The wrong role gets `403`. Fields such as `performed_by`, `ordered_by`, `recorded_by` and `resulted_by` are filled in from the logged-in user.

## Endpoints

Most resources have `GET /x` (list, with filters as query parameters, e.g. `/vital-signs?visit_id=1`), `GET /x/{id}`, `POST /x` and `PATCH /x/{id}`. Setup tables also have `DELETE`. See `/docs` for the request and response fields.

| Area | Paths |
|---|---|
| Auth | `/auth/login`, `/auth/me` |
| Price lists | `/procedures`, `/medications`, `/lab-tests`, `/consumables` |
| Hospital structure | `/departments`, `/staff`, `/doctors`, `/wards`, `/rooms`, `/beds`, `/beds/free` |
| Patients | `/patients`, `/insurance-providers`, `/insurance-policies` |
| Clinical | `/visits`, `/bed-assignments`, `/diagnoses`, `/procedure-history`, `/prescriptions`, `/lab-orders`, `/lab-results`, `/vital-signs`, `/consumable-usage` |
| Billing | `/invoices`, `/invoice-lines`, `/payments`, `/insurance-claims` |

Steps that change a status have their own action endpoints, so the ordering rules in `../docs/entities.md` are always followed:

| Action | Endpoint | Who | Rule |
|---|---|---|---|
| Book a visit | `POST /visits` | receptionist | Status `booked`, needs `planned_start` |
| Check in | `POST /visits/{id}/check-in` | receptionist, nurse | `booked` → `in progress` |
| Admit to a bed | `POST /bed-assignments` | receptionist, nurse | Visit must be inpatient and in progress, bed must be free |
| Transfer | `POST /bed-assignments/{id}/transfer` | receptionist, nurse | Closes the old stay and opens the new one at the same time |
| Discharge | `POST /visits/{id}/discharge` | doctor | Closes the open bed stay, then sets the visit to `completed` |
| Enter a lab result | `POST /lab-results` | lab | Sets the lab order to `completed` |
| Create an invoice | `POST /invoices` | receptionist | Only for a completed visit; status `draft`, number `INV-YYYY-NNNNNN` |
| Add a line | `POST /invoice-lines` | receptionist | Only while `draft` (see below) |
| Issue | `POST /invoices/{id}/issue` | receptionist | `draft` → `issued` |
| Claim | `POST /insurance-claims` | receptionist | Invoice issued; the policy is the patient's and valid on the visit date; amount ≤ total |
| Approve / pay a claim | `POST /insurance-claims/{id}/approve`, `/pay` | receptionist | Paying can set the invoice to `paid` |
| Payment | `POST /payments` | receptionist | Invoice issued, amount ≤ balance; sets the invoice to `paid` at zero balance |

### Invoice lines

- **With a source** (`source_type` = `bed_assignment`, `lab_order` or `consumable_usage`, plus `source_id`): the backend fills in the description, quantity and unit price itself (bed days × room daily rate, lab test price, consumable quantity × price). Each source can be billed only once.
- **Without a source** (consultation, procedures, medication): send `description`, `quantity` and `unit_price`.

`GET /invoices/{id}` returns the lines and the derived `total`, `paid_claims`, `payments` and `balance` (balance = total − paid claims − payments). These figures are calculated, never stored.

## Project layout

```
backend/
  app/
    main.py        FastAPI app; creates tables on startup and includes the routers
    database.py    SQLite engine, session, get_db
    models.py      the 26 SQLAlchemy models (columns and checks from docs/entities/)
    security.py    password hashing, login tokens, role checks
    crud.py        shared helpers: get / list / create / update / delete
    billing.py     invoice totals, balance, bed-day rule, invoice numbers
    schemas/       Pydantic request and response models, one file per area
    routers/       endpoints: auth, ref, org, patients, clinical, billing
  tests/           journey test, CSV seeder test
  seed.py          creates the admin login (admin / admin123)
  seed_csv.py      loads CSV files (default: ../data/) into the database
  requirements.txt
```
