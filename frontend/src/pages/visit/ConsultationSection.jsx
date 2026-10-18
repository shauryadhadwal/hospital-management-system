// Consultation: the doctor writes the chief complaint, the notes and the visit type.
// Saving uses PATCH /visits/{id}, which changes only the fields it is sent.
// Everybody else sees the same text, read only.

import { useEffect, useState } from "react";
import { apiPatch } from "../../api.js";

// Copies the visit's values into the shape of the form.
// "a || b" means: a if it has a value, otherwise b. So a null note (nothing written yet) shows as an empty box.
function fromVisit(visit) {
  return {
    visit_type: visit.visit_type,
    chief_complaint: visit.chief_complaint || "",
    notes: visit.notes || "",
  };
}

// The props are the values this section is given by VisitPage: { visit, staff, names, onChange }.
// names is not used here; every section gets the same props so VisitPage can pass them all the same way.
export default function ConsultationSection({ visit, staff, onChange }) {
  const [form, setForm] = useState(fromVisit(visit)); // the starting value of the form
  const [error, setError] = useState("");

  // Copy the saved values into the form again when the visit is reloaded.
  // The dependency is visit.updated_at, so it only changes when the visit itself has changed
  // (not when a vital sign or lab order is added), and typing in the form is not wiped by other sections.
  useEffect(() => {
    setForm(fromVisit(visit));
  }, [visit.updated_at]);

  // Only the doctor, and only while the visit is in progress, can write the consultation.
  const canWrite = visit.status === "in progress" && staff.role === "doctor";

  async function save(event) {
    event.preventDefault(); // stop the browser reloading the page
    setError("");
    try {
      // Empty text is sent as null, so "no value" is stored instead of an empty text.
      await apiPatch("/visits/" + visit.id, {
        ...form, // copy every field of the form...
        chief_complaint: form.chief_complaint || null, // ...then replace these two with the cleaned values
        notes: form.notes || null,
      });
      onChange(); // ask VisitPage to reload the visit, so every section shows the new data
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="card">
      <h2>Consultation</h2>
      {/* "condition ? A : B" shows A when the condition is true and B when it is false. */}
      {canWrite ? (
        <form className="form" onSubmit={save}>
          <label>
            Chief complaint
            <input
              value={form.chief_complaint}
              onChange={(e) => setForm({ ...form, chief_complaint: e.target.value })}
            />
          </label>
          <label>
            Visit type
            <select value={form.visit_type} onChange={(e) => setForm({ ...form, visit_type: e.target.value })}>
              <option value="outpatient">outpatient</option>
              <option value="inpatient">inpatient</option>
            </select>
          </label>
          <label>
            Notes
            {/* A <textarea> is a box for several lines of text. rows sets how tall it is. */}
            <textarea rows="5" value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
          </label>
          <button type="submit">Save consultation</button>
          {error && <p className="error">{error}</p>}
        </form>
      ) : (
        <div>
          <p>Chief complaint: {visit.chief_complaint || "-"}</p>
          <p>Visit type: {visit.visit_type}</p>
          <p>Notes: {visit.notes || "-"}</p>
        </div>
      )}
    </div>
  );
}
