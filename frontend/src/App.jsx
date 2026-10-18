// The top of the app. It remembers who is logged in and picks which page to show for the current URL.

import { useEffect, useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { apiGet, clearToken, getToken } from "./api.js";
import Layout from "./components/Layout.jsx";
import BillingPage from "./pages/BillingPage.jsx";
import InvoicePage from "./pages/InvoicePage.jsx";
import LabPage from "./pages/LabPage.jsx";
import LoginPage from "./pages/LoginPage.jsx";
import PatientsPage from "./pages/PatientsPage.jsx";
import VisitPage from "./pages/VisitPage.jsx";
import VisitsPage from "./pages/VisitsPage.jsx";

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
        {/* ":id" in a path is a placeholder. /visits/5 matches it with id = "5" and the page reads it with useParams(). */}
        <Route path="/patients" element={<PatientsPage staff={staff} />} />
        <Route path="/visits" element={<VisitsPage staff={staff} />} />
        <Route path="/visits/:id" element={<VisitPage staff={staff} />} />
        <Route path="/lab" element={<LabPage staff={staff} />} />
        <Route path="/billing" element={<BillingPage staff={staff} />} />
        <Route path="/billing/:id" element={<InvoicePage staff={staff} />} />
        {/* Any other URL (including /login) sends you back to the home page. */}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </Layout>
  );
}

// The menu item to start with for each role. Home shows it.
const START_HERE = {
  receptionist: "Patients. Find or register the patient, then book a visit.",
  nurse: "Visits. Open a visit and check the patient in, then record vitals.",
  doctor: "Visits. Open an in-progress visit to consult, order tests and prescribe.",
  lab: "Lab orders. Enter the result for each order.",
  admin: "Patients or Visits to look around. Billing is view only. Set up data in Swagger at /docs.",
};

// A small welcome page. It tells the user which menu item to start with.
function Home({ staff }) {
  return (
    <div>
      <h1>Welcome, {staff.first_name}</h1>
      <p>Start with: {START_HERE[staff.role]}</p>
    </div>
  );
}
