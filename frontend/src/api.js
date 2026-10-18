// Every call to the backend goes through this file.
// It adds the login token to each request and turns backend errors into readable messages,
// so the pages never have to deal with those details.

const TOKEN_KEY = "token";

// localStorage is a small key-value store inside the browser. Values survive a page reload.
export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

// FastAPI puts the reason for an error in "detail". It is usually a string,
// but for invalid input (status 422) it is a list of problems, one per field.
function errorMessage(body, status) {
  if (body && typeof body.detail === "string") return body.detail;
  if (body && Array.isArray(body.detail)) {
    return body.detail.map((d) => `${d.loc.slice(1).join(".")}: ${d.msg}`).join("; ");
  }
  return `Request failed (${status})`;
}

// Turn the JSON text in a reply back into a JavaScript object.
// If the reply is not JSON (for example the backend is not running), return null instead of crashing.
async function readJson(response) {
  try {
    return await response.json();
  } catch {
    return null;
  }
}

// The shared helper behind apiGet, apiPost, apiPatch and apiDelete.
// "async" means the function can wait for slow things (like the network) using "await".
// It returns a Promise: a value that arrives later. Callers also use "await" to get it.
async function request(method, path, data) {
  const headers = {};
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`; // how FastAPI knows who we are

  let body;
  if (data !== undefined) {
    headers["Content-Type"] = "application/json";
    body = JSON.stringify(data); // turn a JavaScript object into JSON text
  }

  // fetch sends an HTTP request. "/api" + path goes through the Vite proxy to FastAPI.
  const response = await fetch("/api" + path, { method, headers, body });

  // 204 means "done, nothing to send back" (used by DELETE).
  if (response.status === 204) return null;

  const result = await readJson(response);

  // response.ok is true for 2xx statuses. Anything else is an error.
  if (!response.ok) {
    // A 401 on a normal call means the token expired or is invalid: forget it and go to login.
    if (response.status === 401 && token) {
      clearToken();
      window.location.href = "/login";
    }
    // "throw" stops the function. The page catches the error and shows error.message.
    throw new Error(errorMessage(result, response.status));
  }
  return result;
}

export const apiGet = (path) => request("GET", path);
export const apiPost = (path, data) => request("POST", path, data ?? {});
export const apiPatch = (path, data) => request("PATCH", path, data);
export const apiDelete = (path) => request("DELETE", path);

// Logging in is the one call that sends form data instead of JSON,
// because FastAPI's OAuth2PasswordRequestForm expects username and password as a form.
export async function login(username, password) {
  const response = await fetch("/api/auth/login", {
    method: "POST",
    body: new URLSearchParams({ username, password }), // encodes as username=...&password=...
  });
  const result = await readJson(response);
  if (!response.ok) throw new Error(errorMessage(result, response.status));
  localStorage.setItem(TOKEN_KEY, result.access_token);
}
