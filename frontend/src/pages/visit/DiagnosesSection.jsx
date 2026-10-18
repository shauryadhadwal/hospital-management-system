// Diagnoses: the doctor writes down what is wrong with the patient. One of them can be marked "primary".

import { useEffect, useState } from "react";
import { apiGet, apiPost } from "../../api.js";

const EMPTY_DIAGNOSIS = { description: "", is_primary: false };

export default function DiagnosesSection({ visit, staff, onChange }) {
  const [rows, setRows] = useState([]);
  const [form, setForm] = useState(EMPTY_DIAGNOSIS);
  const [error, setError] = useState("");

  // Runs when the page opens and whenever the visit is reloaded.
  useEffect(() => {
    apiGet("/diagnoses?visit_id=" + visit.id)
      .then(setRows)
      .catch((err) => setError(err.message));
  }, [visit]);

  // Only the doctor writes diagnoses, and only while the visit is in progress.
  const canWrite = visit.status === "in progress" && staff.role === "doctor";

  async function save(event) {
    event.preventDefault();
    setError("");
    try {
      await apiPost("/diagnoses", {
        visit_id: visit.id,
        description: form.description,
        is_primary: form.is_primary, // already true or false, because it comes from a checkbox
      });
      setForm(EMPTY_DIAGNOSIS);
      onChange();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="card">
      <h2>Diagnoses</h2>
      <table className="table">
        <thead>
          <tr>
            <th>Description</th>
            <th>Primary</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id}>
              <td>{r.description}</td>
              <td>{r.is_primary ? "Yes" : "No"}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {canWrite && (
        <form className="row" onSubmit={save}>
          <label>
            Description
            <input
              required
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
            />
          </label>
          <label>
            {/* A checkbox is on or off. Its change gives e.target.checked, which is true or false (not text). */}
            <input
              type="checkbox"
              checked={form.is_primary}
              onChange={(e) => setForm({ ...form, is_primary: e.target.checked })}
            />
            Primary
          </label>
          <button type="submit">Add diagnosis</button>
        </form>
      )}
      {error && <p className="error">{error}</p>}
    </div>
  );
}
