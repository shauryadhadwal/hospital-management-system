// Procedures: the doctor records the procedures done during this visit.
// Each record also says which doctor performed it. That id is a doctor id, so the name comes from names.doctors.

import { useEffect, useState } from "react";
import { apiGet, apiPost } from "../../api.js";
import { formatDateTime } from "../../format.js";

export default function ProceduresSection({ visit, staff, names, onChange }) {
  const [rows, setRows] = useState([]); // this visit's procedure records
  const [procedures, setProcedures] = useState([]); // the procedure list, for the dropdown and the names
  const [procedureId, setProcedureId] = useState("");
  const [error, setError] = useState("");

  // The procedure list is loaded once.
  useEffect(() => {
    apiGet("/procedures")
      .then(setProcedures)
      .catch((err) => setError(err.message));
  }, []);

  // This visit's records are loaded again each time the visit is reloaded.
  useEffect(() => {
    apiGet("/procedure-history?visit_id=" + visit.id)
      .then(setRows)
      .catch((err) => setError(err.message));
  }, [visit]);

  // .find returns the first procedure whose id matches, or undefined if none does.
  function procedureName(id) {
    const procedure = procedures.find((p) => p.id === id);
    return procedure ? procedure.name : "";
  }

  // Only the doctor records procedures, and only while the visit is in progress.
  const canWrite = visit.status === "in progress" && staff.role === "doctor";

  async function save(event) {
    event.preventDefault();
    setError("");
    try {
      // performed_at is left out, so the backend uses the current time.
      await apiPost("/procedure-history", { visit_id: visit.id, procedure_id: Number(procedureId) });
      setProcedureId("");
      onChange();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="card">
      <h2>Procedures</h2>
      <table className="table">
        <thead>
          <tr>
            <th>Procedure</th>
            <th>Performed at</th>
            <th>Performed by</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id}>
              <td>{procedureName(r.procedure_id)}</td>
              <td>{formatDateTime(r.performed_at)}</td>
              <td>{names.doctors[r.performed_by]}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {canWrite && (
        <form className="row" onSubmit={save}>
          <label>
            Procedure
            <select required value={procedureId} onChange={(e) => setProcedureId(e.target.value)}>
              <option value="">Choose…</option>
              {procedures.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
          </label>
          <button type="submit">Record procedure</button>
        </form>
      )}
      {error && <p className="error">{error}</p>}
    </div>
  );
}
