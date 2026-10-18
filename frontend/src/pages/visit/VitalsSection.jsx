// Vital signs: the nurse or doctor records measurements for this visit, and the list shows every reading so far.

import { useEffect, useState } from "react";
import { apiGet, apiPost } from "../../api.js";
import { formatDateTime } from "../../format.js";

// The form's starting values: every box empty.
const EMPTY_VITALS = {
  temperature_c: "",
  pulse_bpm: "",
  systolic_bp: "",
  diastolic_bp: "",
  respiratory_rate: "",
  oxygen_saturation: "",
};

// An empty box means "not measured", so it is sent as null. A box with text is turned into a number,
// because Number("") would give 0, which would look like a real reading.
function toNumberOrNull(text) {
  return text === "" ? null : Number(text);
}

export default function VitalsSection({ visit, staff, names, onChange }) {
  const [rows, setRows] = useState([]); // the readings for this visit
  const [form, setForm] = useState(EMPTY_VITALS);
  const [error, setError] = useState("");

  // Runs when the page opens and again each time VisitPage reloads the visit (visit changes).
  useEffect(() => {
    apiGet("/vital-signs?visit_id=" + visit.id)
      .then(setRows)
      .catch((err) => setError(err.message));
  }, [visit]);

  // Nurses and doctors can record vitals, and only while the visit is in progress.
  // ["nurse", "doctor"].includes(staff.role) asks "is the role in this list?". It is true for a nurse or a doctor.
  // (Python's version would be: staff.role in ["nurse", "doctor"].)
  const canWrite = visit.status === "in progress" && ["nurse", "doctor"].includes(staff.role);

  async function save(event) {
    event.preventDefault();
    setError("");
    try {
      await apiPost("/vital-signs", {
        visit_id: visit.id,
        temperature_c: toNumberOrNull(form.temperature_c),
        pulse_bpm: toNumberOrNull(form.pulse_bpm),
        systolic_bp: toNumberOrNull(form.systolic_bp),
        diastolic_bp: toNumberOrNull(form.diastolic_bp),
        respiratory_rate: toNumberOrNull(form.respiratory_rate),
        oxygen_saturation: toNumberOrNull(form.oxygen_saturation),
      });
      setForm(EMPTY_VITALS); // clear the boxes for the next reading
      onChange();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="card">
      <h2>Vitals</h2>
      <table className="table">
        <thead>
          <tr>
            <th>Recorded at</th>
            <th>By</th>
            <th>Temp (°C)</th>
            <th>Pulse</th>
            <th>BP (sys/dia)</th>
            <th>Resp rate</th>
            <th>SpO2 (%)</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id}>
              <td>{formatDateTime(r.recorded_at)}</td>
              {/* recorded_by is a staff id, so the name comes from the staff lookup. */}
              <td>{names.staff[r.recorded_by]}</td>
              <td>{r.temperature_c}</td>
              <td>{r.pulse_bpm}</td>
              {/* Show "120/80" only when both numbers are there. */}
              <td>{r.systolic_bp && r.diastolic_bp ? r.systolic_bp + "/" + r.diastolic_bp : ""}</td>
              <td>{r.respiratory_rate}</td>
              <td>{r.oxygen_saturation}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {canWrite && (
        <form className="row" onSubmit={save}>
          <label>
            Temp (°C)
            {/* type="number" lets the browser accept only numbers. step="0.1" allows one decimal place. */}
            <input
              type="number"
              step="0.1"
              value={form.temperature_c}
              onChange={(e) => setForm({ ...form, temperature_c: e.target.value })}
            />
          </label>
          <label>
            Pulse
            <input type="number" value={form.pulse_bpm} onChange={(e) => setForm({ ...form, pulse_bpm: e.target.value })} />
          </label>
          <label>
            BP systolic
            <input
              type="number"
              value={form.systolic_bp}
              onChange={(e) => setForm({ ...form, systolic_bp: e.target.value })}
            />
          </label>
          <label>
            BP diastolic
            <input
              type="number"
              value={form.diastolic_bp}
              onChange={(e) => setForm({ ...form, diastolic_bp: e.target.value })}
            />
          </label>
          <label>
            Resp rate
            <input
              type="number"
              value={form.respiratory_rate}
              onChange={(e) => setForm({ ...form, respiratory_rate: e.target.value })}
            />
          </label>
          <label>
            SpO2 (%)
            <input
              type="number"
              value={form.oxygen_saturation}
              onChange={(e) => setForm({ ...form, oxygen_saturation: e.target.value })}
            />
          </label>
          <button type="submit">Record vitals</button>
        </form>
      )}
      {error && <p className="error">{error}</p>}
    </div>
  );
}
