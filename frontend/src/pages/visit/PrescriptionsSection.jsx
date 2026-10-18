// Prescriptions: the doctor prescribes medicines for this visit. The medicine is picked from the medication list.

import { useEffect, useState } from "react";
import { apiGet, apiPost } from "../../api.js";

const EMPTY_PRESCRIPTION = { medication_id: "", dose: "", frequency: "", duration_days: "", quantity: "" };

export default function PrescriptionsSection({ visit, staff, onChange }) {
  const [rows, setRows] = useState([]); // this visit's prescriptions
  const [medications, setMedications] = useState([]); // the medication list, for the dropdown and names
  const [form, setForm] = useState(EMPTY_PRESCRIPTION);
  const [error, setError] = useState("");

  // The medication list is loaded once.
  useEffect(() => {
    apiGet("/medications")
      .then(setMedications)
      .catch((err) => setError(err.message));
  }, []);

  // This visit's prescriptions are loaded again each time the visit is reloaded.
  useEffect(() => {
    apiGet("/prescriptions?visit_id=" + visit.id)
      .then(setRows)
      .catch((err) => setError(err.message));
  }, [visit]);

  // Writes a medication as "Paracetamol 500mg (tablet)". .find returns the first match.
  function medicationLabel(id) {
    const med = medications.find((m) => m.id === id);
    return med ? `${med.name} ${med.strength} (${med.form})` : "";
  }

  // Only the doctor prescribes, and only while the visit is in progress.
  const canWrite = visit.status === "in progress" && staff.role === "doctor";

  async function save(event) {
    event.preventDefault();
    setError("");
    try {
      // The boxes hold text, so the numbers are converted with Number(...).
      await apiPost("/prescriptions", {
        visit_id: visit.id,
        medication_id: Number(form.medication_id),
        dose: form.dose,
        frequency: form.frequency,
        duration_days: Number(form.duration_days),
        quantity: Number(form.quantity),
      });
      setForm(EMPTY_PRESCRIPTION);
      onChange();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="card">
      <h2>Prescriptions</h2>
      <table className="table">
        <thead>
          <tr>
            <th>Medication</th>
            <th>Dose</th>
            <th>Frequency</th>
            <th>Days</th>
            <th>Quantity</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id}>
              <td>{medicationLabel(r.medication_id)}</td>
              <td>{r.dose}</td>
              <td>{r.frequency}</td>
              <td>{r.duration_days}</td>
              <td>{r.quantity}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {canWrite && (
        <form className="row" onSubmit={save}>
          <label>
            Medication
            <select
              required
              value={form.medication_id}
              onChange={(e) => setForm({ ...form, medication_id: e.target.value })}
            >
              <option value="">Choose…</option>
              {medications.map((m) => (
                <option key={m.id} value={m.id}>
                  {medicationLabel(m.id)}
                </option>
              ))}
            </select>
          </label>
          <label>
            Dose
            <input required value={form.dose} onChange={(e) => setForm({ ...form, dose: e.target.value })} />
          </label>
          <label>
            Frequency
            <input required value={form.frequency} onChange={(e) => setForm({ ...form, frequency: e.target.value })} />
          </label>
          <label>
            Days
            <input
              type="number"
              min="1"
              required
              value={form.duration_days}
              onChange={(e) => setForm({ ...form, duration_days: e.target.value })}
            />
          </label>
          <label>
            Quantity
            <input
              type="number"
              min="1"
              required
              value={form.quantity}
              onChange={(e) => setForm({ ...form, quantity: e.target.value })}
            />
          </label>
          <button type="submit">Prescribe</button>
        </form>
      )}
      {error && <p className="error">{error}</p>}
    </div>
  );
}
