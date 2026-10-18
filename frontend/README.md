# Hospital Management System — Frontend

A React app for the backend in `../backend/`. Staff log in and see a menu for their role (admin, receptionist, nurse, doctor, lab). It runs locally only. Happy path only.

For a primer on HTML, CSS, JavaScript and React, a tour of every file, step-by-step traces of a login and a check-in, and a walkthrough of Peehu's journey in the browser, see [`../docs/frontend.md`](../docs/frontend.md).

## Requirements

- Node.js 18 or later (includes `npm`). Check with `node -v`.
- The backend running on http://127.0.0.1:8000 (see `../backend/README.md`)

## Setup

```bash
cd frontend
npm install
```

This downloads React, React Router and Vite into `node_modules/`. Run it again whenever `package.json` changes.

## Run

Start the backend first, in its own terminal:

```bash
cd backend
.venv/bin/uvicorn app.main:app --reload
```

Then start the frontend:

```bash
cd frontend
npm run dev
```

Open http://localhost:5173 and log in as **admin / admin123**. This login is created by `backend/seed.py`. The staff loaded by `seed_csv.py` from `data/staff.csv` (e.g. `reception.meera`, `dr.rao`, `nurse.anita`, `lab.ravi`) log in with `password`. See `backend/README.md`.

Stop either server with `Ctrl+C`. Saved changes to files in `src/` show up in the browser straight away, with no restart needed.

## How it talks to the backend

The browser only talks to the Vite dev server on port 5173. Any request whose path starts with `/api` is forwarded to the backend, with the `/api` removed. For example, `/api/auth/me` goes to `http://localhost:8000/auth/me`. This is set up in `vite.config.js`. Because of it, the backend needs no CORS settings.

All backend calls go through `src/api.js`. It adds the login token (`Authorization: Bearer ...`) and turns backend errors into messages that are shown on the page. The token is kept in the browser's `localStorage`, so a page reload keeps you logged in. **Log out** clears it.

## Troubleshooting

| What you see | Cause and fix |
|---|---|
| Login shows "Request failed (500)" or similar | The backend is not running. Start it on port 8000. |
| "Incorrect username or password" | Wrong login, or that staff member has no login enabled. |
| `npm run dev` says `vite: command not found` | Run `npm install` first. |
| Port 5173 already in use | Another copy is still running. Stop it with `Ctrl+C`. |
| Stuck on an old login after resetting the database | Click **Log out**, or clear the site data in the browser. |

## Project layout

```
frontend/
  index.html            the single HTML page; loads src/main.jsx
  vite.config.js        dev server settings and the /api proxy
  package.json          libraries and the "npm run dev" command
  src/
    main.jsx            starts React and the router
    App.jsx             who is logged in; the routes (URL to page)
    api.js              every call to the backend
    names.js            loads patient, doctor and staff names for display
    format.js           dates and money as text for the screen
    styles.css          all styling
    components/
      Layout.jsx        header: menu per role, name, logout
    pages/
      LoginPage.jsx     login form
      PatientsPage.jsx  search patients, register, add policy, book a visit
      VisitsPage.jsx    list of visits, filter by status
      VisitPage.jsx     one visit: check-in, discharge, and its sections
      visit/            one component per visit section (vitals, lab orders, bed stay, ...)
      LabPage.jsx       lab: enter the result for each ordered test
      BillingPage.jsx   finished visits to bill, and the invoices
      InvoicePage.jsx   one invoice: lines, insurance claims, payments
```

All three stages are built: login (stage 1), patients, visits and lab (stage 2), and billing (stage 3). See `../docs/frontend.md` for what each file does and the walkthrough of Peehu's journey in the browser.
