# Frontend

A React app in `frontend/` that lets each staff role run Peehu's journey from a browser. It runs locally only, next to the FastAPI backend.

It is built in stages:

1. **Foundation (done):** login, logout, header with a menu per role.
2. **Booking and clinical (next):** patients, visits, one visit's details, lab orders.
3. **Billing:** invoices, claims, payments.

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

### CSS
CSS describes how things look. A rule picks elements with a **selector** and sets **properties**:

```css
.error { color: red; }   /* every element with class "error" turns red */
```

`display: flex` lines children up in a row (or a column with `flex-direction: column`). That one idea covers almost all the layout in `styles.css`.

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

### React
- A **component** is a function that returns **JSX**: HTML-like markup inside JavaScript. `{...}` inside JSX inserts a JavaScript value: `<h1>Welcome, {staff.first_name}</h1>`. JSX writes `className` instead of `class`.
- **Props** are the inputs to a component, passed like attributes: `<LoginPage onLogin={setStaff} />`. Inside, the component reads them as `function LoginPage({ onLogin })`.
- **State** (`useState`) is a value the component remembers. `const [error, setError] = useState("")`. Calling `setError("x")` makes React run the component again and update the screen. You never change the page by hand. You change state, and React redraws.
- **Effects** (`useEffect`) run code after drawing, for example loading data from the backend once when a page opens.
- **Routing** (`react-router-dom`) shows a different component for each URL (`/`, `/patients`, …) without reloading the page.

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
| `src/App.jsx` | Keeps the logged-in staff member in state. On start, it checks a saved token with `/auth/me`. Shows `LoginPage` when no one is logged in, and otherwise `Layout` plus the page for the URL. |
| `src/api.js` | The only file that talks to the backend. `apiGet` / `apiPost` / `apiPatch` / `apiDelete` add the `Authorization: Bearer <token>` header, send JSON, and turn FastAPI errors (`detail`) into messages. `login` sends the form-encoded login request and saves the token. |
| `src/pages/LoginPage.jsx` | The username and password form. On submit it calls `login`, then `/auth/me`, then hands the result to `App` through the `onLogin` prop. |
| `src/components/Layout.jsx` | The header: menu links for the user's role (the `MENU` table), name, role and a logout button. Then the current page. |
| `src/styles.css` | All styling, with a few simple class names. |

`node_modules/` holds downloaded libraries. You never edit it, and it is not committed to git (see `frontend/.gitignore`).

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
