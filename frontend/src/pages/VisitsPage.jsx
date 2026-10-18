// The list of visits, with a filter by status. Each visit id links to its visit page.

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { apiGet } from "../api.js";
import { formatDateTime } from "../format.js";
import { loadNames } from "../names.js";

// The status choices for the filter dropdown. "all" means no filter.
const STATUSES = ["all", "booked", "in progress", "completed"];

export default function VisitsPage() {
  const [status, setStatus] = useState("all"); // the filter the user picked
  const [visits, setVisits] = useState([]);
  // Starts as empty lookups, so the table can be drawn before the names arrive.
  const [names, setNames] = useState({ patients: {}, doctors: {}, staff: {} });
  const [error, setError] = useState("");

  // Names are loaded once, when the page opens.
  useEffect(() => {
    loadNames()
      .then(setNames)
      .catch((err) => setError(err.message));
  }, []);

  // The visit list is loaded when the page opens and again every time the filter changes.
  // The [status] at the end is the list of values that trigger the effect.
  useEffect(() => {
    // With "all" there is no filter. Otherwise add ?status=... (encoded, so "in progress" becomes "in%20progress").
    const query = status === "all" ? "" : "?status=" + encodeURIComponent(status);
    apiGet("/visits" + query)
      .then(setVisits)
      .catch((err) => setError(err.message));
  }, [status]);

  return (
    <div>
      <h1>Visits</h1>
      {error && <p className="error">{error}</p>}

      <div className="card">
        {/* A <select> dropdown. onChange runs each time the user picks another option. */}
        <label>
          Status{" "}
          <select value={status} onChange={(e) => setStatus(e.target.value)}>
            {STATUSES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </label>

        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Patient</th>
              <th>Doctor</th>
              <th>Type</th>
              <th>Status</th>
              <th>Planned start</th>
            </tr>
          </thead>
          <tbody>
            {visits.map((v) => (
              <tr key={v.id}>
                <td>
                  <Link to={"/visits/" + v.id}>{v.id}</Link>
                </td>
                <td>{names.patients[v.patient_id]}</td>
                <td>{names.doctors[v.doctor_id]}</td>
                <td>{v.visit_type}</td>
                <td>
                  <span className={"badge " + v.status.replace(" ", "-")}>{v.status}</span>
                </td>
                <td>{formatDateTime(v.planned_start)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
