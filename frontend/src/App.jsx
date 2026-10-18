// The top of the app. It remembers who is logged in and picks which page to show for the current URL.

import { useEffect, useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { apiGet, clearToken, getToken } from "./api.js";
import Layout from "./components/Layout.jsx";
import LoginPage from "./pages/LoginPage.jsx";

// A component is a function that returns JSX: HTML-like markup that React turns into real page elements.
// Component names start with a capital letter, and you use them like tags: <App />.
export default function App() {
  // useState gives a component a value to remember, plus a function to change it.
  // Calling setStaff(...) makes React run this function again and redraw with the new value.
  const [staff, setStaff] = useState(null); // the logged-in staff member, or null
  const [loading, setLoading] = useState(true); // true while we check a saved token

  // useEffect runs code after the component is drawn. The empty list [] means "only once, at the start".
  // If a token was saved by an earlier login, ask the backend who it belongs to.
  useEffect(() => {
    if (!getToken()) {
      setLoading(false);
      return;
    }
    apiGet("/auth/me")
      .then((me) => setStaff(me)) // .then runs when the request succeeds
      .catch(() => clearToken()) // .catch runs when it fails, for example an expired token
      .finally(() => setLoading(false)); // .finally runs either way
  }, []);

  function logout() {
    clearToken();
    setStaff(null);
  }

  if (loading) return <p className="page">Loading…</p>;

  // Not logged in: every URL shows the login page.
  // onLogin is a "prop": a value passed into a component, like an argument to a function.
  if (!staff) return <LoginPage onLogin={setStaff} />;

  // Logged in: <Routes> shows the first <Route> whose path matches the URL.
  return (
    <Layout staff={staff} onLogout={logout}>
      <Routes>
        <Route path="/" element={<Home staff={staff} />} />
        {/* Any other URL (including /login) sends you back to the home page. */}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </Layout>
  );
}

// A small welcome page. The real pages are added in later stages.
function Home({ staff }) {
  return (
    <div>
      <h1>Welcome, {staff.first_name}</h1>
      <p>Use the menu above to get started.</p>
    </div>
  );
}
