# Hospital Management System

A college project: a small hospital system that follows one patient, Peehu, from booking to final payment. The project is built design first. It runs locally only.

| Folder | What is in it |
|---|---|
| `docs/` | The design: 26 entities, Peehu's user journey, personas, and the frontend guide |
| `data/` | Sample data as CSV files, one per entity |
| `backend/` | FastAPI + SQLite API with role-based login. See [`backend/README.md`](backend/README.md) |
| `frontend/` | React app for staff. See [`frontend/README.md`](frontend/README.md) |

## Quick start

You need Python 3.9+ and Node.js 18+.

**1. Backend** (terminal 1):

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python seed_csv.py                # loads data/*.csv; staff log in with password
.venv/bin/python seed.py                    # adds the admin login: admin / admin123
.venv/bin/uvicorn app.main:app --reload     # http://127.0.0.1:8000 (API docs at /docs)
```

**2. Frontend** (terminal 2):

```bash
cd frontend
npm install
npm run dev                                 # http://localhost:5173
```

Open http://localhost:5173 and log in as **admin / admin123**, or as any staff member from `data/staff.csv` (e.g. `reception.meera`, `dr.rao`) with `password`. See [`backend/README.md`](backend/README.md#seed-the-database).

After the first run, you only need to repeat the last command in each terminal: `uvicorn ...` and `npm run dev`.

## Where to read next

- [`docs/user_journey.md`](docs/user_journey.md): the story the whole system is built around
- [`docs/entities.md`](docs/entities.md): the data model and ordering rules
- [`docs/frontend.md`](docs/frontend.md): how the frontend works, for readers new to JavaScript
- `cd backend && .venv/bin/pytest -q`: runs Peehu's whole journey through the API as a test
