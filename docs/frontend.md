# Frontend

A React app in `frontend/` that lets each staff role run Peehu's journey from a browser. It runs locally only, next to the FastAPI backend.

It is built in stages:

1. **Foundation (done):** login, logout, header with a menu per role.
2. **Booking and clinical (done):** patients (search, register, insurance policy, book a visit), the visit list, one visit page with its sections (check-in, consultation, vitals, lab orders, procedures, consumables, diagnoses, bed stay for inpatients, prescriptions, discharge), and the lab orders page where the lab enters results.
3. **Billing (done):** the billing list (create an invoice for a finished visit) and the invoice page (add lines, issue, insurance claims, payments).

## Running it

For full setup and troubleshooting, see `frontend/README.md`. In short, you need two terminals, one for each server.

```bash
# Terminal 1: backend on http://localhost:8000
cd backend
.venv/bin/python seed.py            # first time only: creates the admin login
.venv/bin/uvicorn app.main:app --reload

# Terminal 2: frontend on http://localhost:5173
cd frontend
npm install                         # first time only: downloads the libraries into node_modules/
npm run dev
```

Open http://localhost:5173 and log in as `admin` / `admin123`.

## Primer: the minimum you need to read this code

### HTML
HTML describes what is on a page, using tags: `<h1>Title</h1>`, `<p>paragraph</p>`, `<button>Click</button>`, `<input />`. Tags can sit inside other tags. Attributes give extra details, for example `<input type="password" />`. Our only real HTML file is `index.html`, and it is almost empty. React builds everything else.

Tables: `<table>` holds `<thead>` (the header row) and `<tbody>` (the data rows). Each `<tr>` is one row, `<th>` is a header cell and `<td>` is a normal cell.

Form controls: `<select>` is a dropdown (each `<option value="...">` is one choice), `<textarea>` is a box for several lines, and `<input type="checkbox">` is an on/off box.

### CSS
CSS describes how things look. A rule picks elements with a **selector** and sets **properties**:

```css
.error { color: red; }   /* every element with class "error" turns red */
```

`display: flex` lines children up in a row (or a column with `flex-direction: column`). That one idea covers almost all the layout in `styles.css`.

A status badge gets its colour from a class name built from the status text. `"in progress"` becomes `badge in-progress`, and `styles.css` has a rule for `.badge.in-progress`.

### JavaScript
These are the parts this code uses:

| Code | Meaning |
|---|---|
| `const x = 5;` / `let y;` | A variable. A `const` cannot be reassigned. |
| `function f(a) { ... }` and `(a) => ...` | Two ways to write a function. The arrow form is shorter. |
| `{ name: "Peehu", age: 20 }` | An object, like a Python dict. Read a value with `obj.name`. |
| `[1, 2, 3]`, `list.map(x => x * 2)` | An array, like a Python list. `.map` builds a new array (a list comprehension). |
| `` `Hello ${name}` `` | A template string, like a Python f-string. |
| `const { a, b } = obj;` | Destructuring: pull `obj.a` and `obj.b` into variables. |
| `import x from "./file.js"` / `export` | Share code between files, like Python imports. |
| `async function` / `await` | Wait for something slow (a network call) without freezing the page. Same idea as Python's `async`/`await`. |
| `try { } catch (err) { }` | Like Python's `try` / `except`. |
| `throw new Error("msg")` | Like Python's `raise Exception("msg")`. |
| `a && b` | If `a` is falsy, the result is `a`; otherwise it is `b`. |
| `a ?? b` | Use `a`, unless it is `null` or `undefined`, in which case use `b`. |
| `cond ? a : b` | If `cond` is true use `a`, otherwise use `b`. Like Python's `a if cond else b`. |
| `list.filter(x => ...)` | A new list with only the items where the test is true. |
| `list.find(x => ...)` | The first item where the test is true, or `undefined` if none is. |
| `list.some(x => ...)` | `true` if at least one item passes the test. |
| `Object.fromEntries([[k, v], ...])` | Turns a list of `[key, value]` pairs into an object. Used for lookup tables. |
| `{ ...obj, age: 5 }` | Object spread: copy every field of `obj`, then set `age`. Later fields win. |
| `{ [id]: text }` | Computed key: the key name is the value of `id`. With `id = 3` this is `{ 3: text }`. |
| `[...a, ...b]` | Array spread: join two lists into one. |
| `Promise.all([...])` | Start several requests at the same time and wait until all of them finish. The results come back in the same order. |

### React
- A **component** is a function that returns **JSX**: HTML-like markup inside JavaScript. `{...}` inside JSX inserts a JavaScript value: `<h1>Welcome, {staff.first_name}</h1>`. JSX writes `className` instead of `class`.
- **Props** are the inputs to a component, passed like attributes: `<LoginPage onLogin={setStaff} />`. Inside, the component reads them as `function LoginPage({ onLogin })`. The spread `<X {...obj} />` passes every field of `obj` as a separate prop.
- **State** (`useState`) is a value the component remembers. `const [error, setError] = useState("")`. Calling `setError("x")` makes React run the component again and update the screen. You never change the page by hand. You change state, and React redraws.
- **Effects** (`useEffect`) run code after drawing, for example loading data from the backend when a page opens. The list at the end is the **dependency list**: the effect runs again only when a value in that list changes. `[]` means "only once".
- **Routing** (`react-router-dom`) shows a different component for each URL (`/`, `/patients`, …) without reloading the page.

More React concepts used by the pages:

| Code | Meaning |
|---|---|
| `useEffect(fn, [visit])` | Run `fn` after drawing, and again each time `visit` changes. |
| `useParams()` | Read the `:id` part of the URL. For `/visits/5` it gives `{ id: "5" }`. |
| `<Link to="/visits">` | An `<a>` tag that changes the page without reloading it. |
| `<NavLink to="/visits">` | Like `Link`, and adds the class `active` when that URL is the current page (used in the header menu). |
| `useNavigate()` | Returns a function that changes the page from code, for example after "Create invoice". |
| `{cond && <X />}` | Show `<X />` only when `cond` is true. |
| `{cond ? <A /> : <B />}` | Show `<A />` when `cond` is true, otherwise `<B />`. |
| `{list.map(x => <li key={x.id}>...</li>)}` | One element per item. `key` is a unique id that lets React track each item. |
| `value={form.x}` and `onChange={e => setForm(...)}` | A **controlled** input: the box shows state, and typing updates state. `e.target.value` is the text. A checkbox uses `checked` and `e.target.checked`. |

## How the pieces connect

```
browser ──► localhost:5173 (Vite dev server)
              ├─ serves index.html and our .jsx/.js files
              └─ /api/...  ──proxy──►  localhost:8000 (FastAPI)
```

The frontend always calls `/api/<backend path>`. Vite removes `/api` and forwards the request to FastAPI. Because the browser only ever talks to one address, the backend needs no CORS setup.

## File tour

| File | What it does |
|---|---|
| `frontend/package.json` | Lists the libraries (React, React Router, Vite) and the `npm run dev` command. |
| `frontend/vite.config.js` | Dev server settings: the React plugin and the `/api` proxy to the backend. |
| `frontend/index.html` | The single HTML page. It has an empty `<div id="root">` and loads `src/main.jsx`. |
| `src/main.jsx` | Starting point. Draws `<App />` inside `#root`, wrapped in `BrowserRouter` so routes work. |
| `src/App.jsx` | Keeps the logged-in staff member in state. On start, it checks a saved token with `/auth/me`. Shows `LoginPage` when no one is logged in. When someone is logged in, it shows `Layout` around the routes: `/` (Home), `/patients`, `/visits`, `/visits/:id`, `/lab`, `/billing`, `/billing/:id`. Any other URL goes to `/`. Home holds the "start here" text for each role. |
| `src/api.js` | The only file that talks to the backend. `apiGet` / `apiPost` / `apiPatch` / `apiDelete` add the `Authorization: Bearer <token>` header, send JSON, and turn FastAPI errors (`detail`) into messages. `login` sends the form-encoded login request and saves the token. |
| `src/format.js` | Helpers that turn backend text into screen text: `formatDateTime` and `formatDate` (the browser's date format) and `formatMoney` (`₹` and two decimals). No backend calls. |
| `src/names.js` | `loadNames()` calls `GET /patients`, `GET /doctors` and `GET /staff` and returns lookups: `names.patients[id]`, `names.doctors[id]` (for example "Dr. Arvind Rao") and `names.staff[id]`. Pages use it to show names instead of ids. |
| `src/pages/LoginPage.jsx` | The username and password form. On submit it calls `login`, then `/auth/me`, then hands the result to `App` through the `onLogin` prop. |
| `src/components/Layout.jsx` | The header: menu links for the user's role (the `MENU` table), name, role and a logout button. Then the current page. Admin and receptionist: Home, Patients, Visits, Billing. Nurse and doctor: Home, Patients, Visits. Lab: Home, Lab orders. |
| `src/pages/PatientsPage.jsx` | Patient search and the selected patient's policies and visits. Calls `GET /patients` (with `?name=`), `GET /insurance-policies?patient_id=`, `GET /visits?patient_id=`, plus `GET /doctors`, `GET /staff` and `GET /insurance-providers` for the dropdowns. Forms: register patient (`POST /patients`), add policy (`POST /insurance-policies`), book visit (`POST /visits`). Only the receptionist sees the forms. Menu: all roles except lab. |
| `src/pages/VisitsPage.jsx` | The list of visits with a status filter. Calls `GET /visits` (with `?status=`) and `loadNames`. Each visit id links to `/visits/:id`. No forms. Menu: admin, receptionist, nurse, doctor. |
| `src/pages/VisitPage.jsx` | One visit at `/visits/:id`: the header, the Check in and Discharge buttons, and the eight sections. Calls `GET /visits/{id}`, `POST /visits/{id}/check-in` (receptionist, nurse) and `POST /visits/{id}/discharge` (doctor). The bed section only shows for inpatient visits. Reached from the Visits and Patients pages. |
| `src/pages/visit/VitalsSection.jsx` | Vitals list and form. Calls `GET /vital-signs?visit_id=` and `POST /vital-signs`. Form: nurse and doctor, while the visit is in progress. |
| `src/pages/visit/ConsultationSection.jsx` | Chief complaint, visit type and notes. Calls `PATCH /visits/{id}`. Form: doctor, while in progress (the doctor can also change the visit type to inpatient). Everyone else sees the text read only. |
| `src/pages/visit/LabSection.jsx` | Lab orders with status and result. Calls `GET /lab-tests`, `GET /lab-orders?visit_id=`, `GET /lab-results?lab_order_id=` (once per order) and `POST /lab-orders`. Form: doctor, while in progress. |
| `src/pages/visit/ProceduresSection.jsx` | Procedures done in this visit and who did them. Calls `GET /procedures`, `GET /procedure-history?visit_id=` and `POST /procedure-history`. Form: doctor, while in progress. |
| `src/pages/visit/ConsumablesSection.jsx` | Items used in this visit, with an optional link to one of its procedures. Calls `GET /consumables`, `GET /procedures`, `GET /consumable-usage?visit_id=`, `GET /procedure-history?visit_id=` and `POST /consumable-usage`. Form: nurse and doctor, while in progress. |
| `src/pages/visit/DiagnosesSection.jsx` | Diagnoses with a "primary" checkbox. Calls `GET /diagnoses?visit_id=` and `POST /diagnoses`. Form: doctor, while in progress. |
| `src/pages/visit/BedSection.jsx` | Bed stays for an inpatient visit. Calls `GET /beds`, `GET /rooms`, `GET /wards`, `GET /beds/free` and `GET /bed-assignments?visit_id=`. Admit uses `POST /bed-assignments`; a move uses `POST /bed-assignments/{id}/transfer`. Form: receptionist and nurse, while in progress. |
| `src/pages/visit/PrescriptionsSection.jsx` | Prescriptions for this visit. Calls `GET /medications`, `GET /prescriptions?visit_id=` and `POST /prescriptions`. Form: doctor, while in progress. |
| `src/pages/LabPage.jsx` | The lab's page at `/lab`. Lists orders still waiting (`GET /lab-orders?status=ordered`) and completed ones (`?status=completed`), with `GET /lab-results`, `GET /visits` and `GET /lab-tests` for the names. Form: a result box per waiting order, `POST /lab-results`. Menu: lab. |
| `src/pages/BillingPage.jsx` | The billing list at `/billing`. Shows completed visits with no invoice yet and all invoices. Calls `GET /visits`, `GET /invoices` and `loadNames`. The "Create invoice" button calls `POST /invoices` and opens the new invoice. Only the receptionist sees the button. Menu: admin (view only) and receptionist. |
| `src/pages/InvoicePage.jsx` | One invoice at `/billing/:id`: header, totals, lines, charges to add, claims and payments. It loads the invoice, its visit and everything the charges come from (bed stays, lab orders, consumable usage, procedures, prescriptions, price lists). Calls `POST /invoice-lines`, `DELETE /invoice-lines/{id}`, `POST /invoices/{id}/issue`, `POST /insurance-claims`, `POST /insurance-claims/{id}/approve`, `POST /insurance-claims/{id}/pay` and `POST /payments`. Only the receptionist sees the forms and buttons: lines while the invoice is a draft, claims and payments while it is issued. Admin sees it read only. |
| `src/styles.css` | All styling: the page, the login form, the header, cards, tables, inline forms (`.row`), status badges (one colour per status), muted text and the invoice summary. |

`node_modules/` holds downloaded libraries. You never edit it, and it is not committed to git (see `frontend/.gitignore`).

## How the visit page refreshes

`VisitPage` loads the visit with `useEffect` (dependency list `[id]`). Every section gets the same props: `visit`, `staff`, `names` and `onChange`, where `onChange` is `VisitPage`'s `reload` function.

- Each section loads its own list in a `useEffect` with the dependency list `[visit]`. That runs when the section opens, and again each time `VisitPage` sets a new `visit` object.
- When a section saves, it calls `onChange()`. `reload` fetches `GET /visits/{id}` and sets the new visit. The header and every section then load again, so all of them show the newest data.
- Catalogue lists (lab tests, procedures, medications, consumables) load once, with the dependency list `[]`. A reload does not fetch them again.
- `ConsultationSection` is the exception. It copies the visit into its form with the dependency list `[visit.updated_at]`. The form is refreshed only when the visit row itself changes, so a save in another section does not wipe what the doctor is typing.

## Tracing one request: logging in

1. You type into the username box. Its `onChange` calls `setUsername`, so React re-draws `LoginPage` with the new value.
2. You click **Log in**. The form's `onSubmit` runs `handleSubmit`, which calls `event.preventDefault()` so the browser does not reload the page.
3. `login(username, password)` in `api.js` runs `fetch("/api/auth/login", { method: "POST", body: URLSearchParams })`.
4. Vite's proxy forwards the request to `http://localhost:8000/auth/login`.
5. FastAPI's `login` in `backend/app/routers/auth.py` checks the password and returns `{ access_token, ... }`. If the password is wrong, it returns 401 with `{"detail": "Incorrect username or password"}`. `login` then throws, and `LoginPage` shows the message in red.
6. `api.js` saves `access_token` in `localStorage`.
7. `LoginPage` calls `apiGet("/auth/me")`. `request` adds `Authorization: Bearer <token>`, and FastAPI's `get_current_staff` (`backend/app/security.py`) decodes the token and returns the staff member.
8. `onLogin(me)` is really `setStaff(me)` in `App`. The state changes, so `App` re-draws, `staff` is no longer `null`, and it shows `Layout` with the menu for `me.role`.
9. On a page reload, the `useEffect` in `App` finds the saved token and calls `/auth/me` again, so you stay logged in. **Log out** deletes the token and sets `staff` back to `null`.

## Tracing one request: checking a visit in

This is what happens when a receptionist or nurse clicks **Check in** on a booked visit.

1. `VisitPage` shows the **Check in** button only when `visit.status` is `"booked"` and the role is receptionist or nurse.
2. Clicking it runs `checkIn()` in `VisitPage.jsx`. It clears the error and calls `apiPost("/visits/" + id + "/check-in")`. No data is passed, so `apiPost` sends `{}` as the body.
3. `request` in `api.js` adds the `Authorization` header and `Content-Type: application/json`, then calls `fetch("/api/visits/5/check-in", { method: "POST" ... })` (for visit 5).
4. Vite's proxy removes `/api` and forwards the request to `http://localhost:8000/visits/5/check-in`.
5. FastAPI runs `check_in_visit` in `backend/app/routers/clinical.py`. `require_roles("receptionist", "nurse")` checks the role. The visit must be `booked`, otherwise the backend returns 400 with a reason. If it is booked, the backend sets `status` to `"in progress"` and `actual_start` to the current time, and returns the visit.
6. Back in `api.js`, the response is OK, so the JSON is returned. `checkIn` then calls `reload()`, which calls `apiGet("/visits/5")` and `setVisit(...)`.
7. React redraws. The badge reads `in progress` (class `badge in-progress`), the **Check in** button is gone, the doctor sees **Discharge**, and the section forms appear, because each section checks `visit.status === "in progress"`.

If the backend refuses the check-in, `request` throws, `checkIn` catches it, and the message is shown in red.

## Walking Peehu's journey in the browser

Start the backend and the frontend first (see **Running it**). Every login uses the password `password`. Between logins, click **Log out** in the top right.

The seed already holds some history. Visit 1 is Peehu's finished inpatient stay (patient 1, Peehu Sharma). Visits 2 to 4 belong to other patients, and visit 5 is a booked follow-up for Rohan Verma with Dr. Iyer. So this walkthrough registers a new patient and follows the stages in `docs/user_journey.md`.

The app records the current time for every action (check-in, admission, transfer, discharge), so the three days of the story happen close together. Each bed stay then bills one day (bed days count calendar dates, minimum 1).

### Stage 1: registration and booking (log in as `reception.meera`)

1. Click **Patients**.
2. Under **Register a new patient**, fill in first name, last name, age, sex and phone. The emergency contact boxes are optional. Click **Register patient**. The new patient opens below.
3. Under **Insurance policies**, choose provider `HealthFirst`, type a policy number, set **Valid from** and **Valid to**, then click **Add policy**.
4. In the **Book visit** form, choose **Doctor** `Dr. Arvind Rao`, keep **Type** as `outpatient`, set **Planned start** and type a **Chief complaint** (for example "Chest pain for two days"). Click **Book visit**. The new visit appears with the badge `booked`.
5. Click **Log out**.

### Stage 2: arrival and consultation

6. Log in as `nurse.anita`. Click **Visits**, then click the new visit's ID (its row is `booked`).
7. Click **Check in**. The badge becomes `in progress`.
8. Under **Vitals**, enter pulse `104` and BP systolic `150`, diastolic `95` (other boxes are optional). Click **Record vitals**. Click **Log out**.
9. Log in as `dr.rao`. Click **Visits** and open the visit.
10. Under **Consultation**, type the chief complaint and notes, then click **Save consultation**.
11. Under **Lab orders**, choose `Troponin` and click **Order test**. Click **Log out**.
12. Log in as `lab.ravi`. Click **Lab orders**. In the row for the Troponin order, type the result (for example "Elevated") and click **Save result**. The order moves to **Completed**. Click **Log out**.
13. Log in as `dr.rao`. Open the visit, go to **Procedures**, choose `ECG` and click **Record procedure**. Click **Log out**.
14. Log in as `nurse.anita`. Open the visit, go to **Consumables**, choose `ECG electrode pack`, quantity `1`, and under **Linked procedure** pick the ECG row. Click **Record usage**. Click **Log out**.
15. Log in as `dr.rao`. Open the visit, go to **Diagnoses**, type `Unstable angina`, tick **Primary**, and click **Add diagnosis**.

### Stage 3: admission

16. Still as `dr.rao`, go to **Consultation**, change **Visit type** to `inpatient`, and click **Save consultation**. A **Bed stay** section appears. Click **Log out**.
17. Log in as `nurse.anita`. Open the visit and go to **Bed stay**. Under **Admit to bed**, choose `ICU / room ICU-1 / bed 1` and click **Admit**.
18. Still as `nurse.anita`, go to **Consumables**, choose `IV set`, quantity `1`, leave **Linked procedure** as `None`, and click **Record usage**.
19. Go to **Bed stay**. Under **Move to bed**, choose `General Ward A / room GA-1 / bed 3` and click **Transfer**. The ICU stay gets an end time and a new stay opens in General Ward A. Click **Log out**.

### Stage 4: treatment and discharge (log in as `dr.rao`)

20. Open the visit and go to **Prescriptions**. Choose `Aspirin 75 mg (tablet)`, fill in dose, frequency, days and quantity, and click **Prescribe**. Repeat for `Atorvastatin 20 mg (tablet)`.
21. Click **Discharge** at the top of the visit and confirm with **OK**. The bed stay closes first, then the visit's status becomes `completed`. Click **Log out**.

### Stage 5: billing and payment (log in as `reception.meera`)

22. Click **Billing**. Under **Ready to bill**, find the patient and click **Create invoice**. The invoice page opens with status `draft`.
23. Under **Charges to add**, click **Add** next to each suggestion until the list says "Nothing else to add": the consultation, the ECG procedure, the Troponin lab test, the two bed stays, the two medications and the two consumables.
24. Click **Issue invoice** and confirm with **OK**. The lines can no longer change, and the status becomes `issued`.
25. Under **Insurance claims**, check the policy, type an **Amount claimed** that is most of the total, and click **Submit claim**.
26. On the submitted claim, click **Approve**, then **Mark paid**. The claim status becomes `paid`.
27. Under **Payments**, the amount is already the balance. Check that **Method** is `UPI`, type the UPI reference, and click **Record payment**. The balance shows `₹0.00` and the invoice status becomes `paid`.

## Stop

Click **Log out**, then stop both servers with `Ctrl+C`.
