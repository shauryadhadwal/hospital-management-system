# Hospital Management System

Design-first project. The design lives in markdown under `docs/`:

- `docs/entities.md`: the 26 entities, key relationships and the happy-path ordering rules.
- `docs/entities/<entity>.md`: one doc per entity (purpose, decisions, columns, constraints, relationships).
- `docs/user_journey.md`: Peehu's stay from booking to payment; every entity is used at least once.
- `docs/personas/`: what each role needs and the gaps.
- `docs/brainstorming.md`: dropped or merged entities and open follow-ups.

## Backend

`backend/` is a FastAPI + SQLAlchemy + SQLite backend with basic CRUD and role checks so the user journey can be run by each persona (admin, receptionist, nurse, doctor, lab). The ordering rules from `docs/entities.md` are enforced in action endpoints (check-in, discharge, transfer, issue, claim approve/pay) and in `backend/app/billing.py`. Python 3.9: use `Optional`/`List`, not `X | None`.

- Setup: `cd backend && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`
- Seed: `.venv/bin/python seed_csv.py` loads `../data/*.csv` (one CSV per table; every staff login's password is `password`, stored in `data/staff.csv` as bcrypt hashes; `--password <pw>` overrides it), then `.venv/bin/python seed.py` adds admin / admin123
- Run: `.venv/bin/uvicorn app.main:app --reload`, then open `/docs`
- Test: `.venv/bin/pytest -q` (`tests/test_journey.py` walks Peehu's whole journey)

## Frontend

`frontend/` is a React app (Vite, plain JavaScript and CSS, `react-router-dom` only), run locally only. It calls the backend via `/api/...`, which the Vite proxy forwards to `localhost:8000`, so there is no CORS. All backend calls go through `src/api.js`. The user is learning JS/HTML/CSS through this code: keep it simple, comment concepts on first use, and keep `docs/frontend.md` (primer, file tour, request trace) in step with the code.

- Setup: `cd frontend && npm install`
- Run (with the backend running): `npm run dev`, then open http://localhost:5173

## Working agreement

- **Design first, implement only after confirmation.** Propose the design, wait for the user's explicit go-ahead, then build. Do not write application code, schemas, migrations or services until the user confirms the design.
- Keep the design basic and satisfactory: cover the core hospital workflows, avoid speculative extras.
- **Happy path only (for now).** Design and document the normal flow only. Do not design rejected claims or resubmissions, cancelled or no-show visits, emergency visits, refunds, or other exception flows until the user asks for them.
- Once a design is confirmed, implement only the confirmed scope; raise anything new as a design question first.
- There is no validator script. After a design change, keep the docs consistent by hand: update the entity doc, `docs/entities.md`, `docs/user_journey.md` (diagram, coverage table, notes) and any affected persona, and check that the entity count and the roles, statuses and `source_type` values match everywhere.
- This is for a college project.
