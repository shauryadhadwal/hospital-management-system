// One visit: its header, the check-in and discharge buttons, and one section per clinical step.
// Each section shows its list to everyone, and its form only to the roles that may write it.

import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { apiGet, apiPost } from "../api.js";
import { formatDateTime } from "../format.js";
import { loadNames } from "../names.js";
import BedSection from "./visit/BedSection.jsx";
import ConsultationSection from "./visit/ConsultationSection.jsx";
import ConsumablesSection from "./visit/ConsumablesSection.jsx";
import DiagnosesSection from "./visit/DiagnosesSection.jsx";
import LabSection from "./visit/LabSection.jsx";
import PrescriptionsSection from "./visit/PrescriptionsSection.jsx";
import ProceduresSection from "./visit/ProceduresSection.jsx";
import VitalsSection from "./visit/VitalsSection.jsx";

export default function VisitPage({ staff }) {
  // useParams reads the ":id" part of the address. For /visits/5 it gives { id: "5" }.
  // The { id } on the left is "destructuring": it takes the id property out of the object.
  const { id } = useParams();
  const [visit, setVisit] = useState(null); // null until the first load has finished
  const [names, setNames] = useState({ patients: {}, doctors: {}, staff: {} });
  const [error, setError] = useState("");

  // Fetches the visit again. Every change on this page calls it, so the header and all sections show the newest data.
  // Setting a new visit object makes each section's useEffect (which depends on visit) load its list again.
  async function reload() {
    try {
      setVisit(await apiGet("/visits/" + id));
    } catch (err) {
      setError(err.message);
    }
  }

  // Runs when the page opens (and again if the id in the address changes).
  useEffect(() => {
    reload();
    loadNames()
      .then(setNames)
      .catch((err) => setError(err.message));
  }, [id]);

  // "Check in" moves a booked visit to in progress. Only the receptionist and the nurse do this.
  // ["receptionist", "nurse"].includes(staff.role) checks whether the role is in that list.
  async function checkIn() {
    setError("");
    try {
      await apiPost("/visits/" + id + "/check-in");
      reload();
    } catch (err) {
      setError(err.message);
    }
  }

  // Discharge ends the visit. window.confirm shows a pop-up with OK and Cancel; it returns true for OK.
  // "return" stops the function here when the user presses Cancel.
  async function discharge() {
    if (!window.confirm("Discharge this patient now?")) return;
    setError("");
    try {
      await apiPost("/visits/" + id + "/discharge");
      reload();
    } catch (err) {
      setError(err.message);
    }
  }

  // Shown until the visit has loaded. If loading failed, the error is shown instead.
  if (!visit) return error ? <p className="error">{error}</p> : <p>Loading…</p>;

  // The props passed to every section: the visit, the logged-in staff member, the name lookups and the reload function.
  const sectionProps = { visit, staff, names, onChange: reload };

  return (
    <div>
      <h1>Visit {visit.id}</h1>
      <p>
        <Link to="/visits">Back to visits</Link>
      </p>
      {error && <p className="error">{error}</p>}

      <div className="card">
        <p>
          Patient: {names.patients[visit.patient_id]} · Doctor: {names.doctors[visit.doctor_id]}
        </p>
        <p>
          Type: {visit.visit_type} · Status:{" "}
          {/* status "in progress" becomes the class "in-progress" (see styles.css). */}
          <span className={"badge " + visit.status.replace(" ", "-")}>{visit.status}</span>
        </p>
        <p>
          Planned start: {formatDateTime(visit.planned_start)} · Actual start: {formatDateTime(visit.actual_start) || "-"}{" "}
          · Actual end: {formatDateTime(visit.actual_end) || "-"}
        </p>
        <p>Chief complaint: {visit.chief_complaint || "-"}</p>
        <p>Notes: {visit.notes || "-"}</p>

        <div className="row">
          {visit.status === "booked" && ["receptionist", "nurse"].includes(staff.role) && (
            <button onClick={checkIn}>Check in</button>
          )}
          {visit.status === "in progress" && staff.role === "doctor" && (
            <button onClick={discharge}>Discharge</button>
          )}
        </div>
      </div>

      {/* Each section is a separate component. "<X {...} />" draws it with the props in sectionProps.
          The spread "{...sectionProps}" passes every value in that object as a separate prop. */}
      <ConsultationSection {...sectionProps} />
      <VitalsSection {...sectionProps} />
      <LabSection {...sectionProps} />
      <ProceduresSection {...sectionProps} />
      <ConsumablesSection {...sectionProps} />
      <DiagnosesSection {...sectionProps} />
      {/* The bed section only exists for inpatient visits. */}
      {visit.visit_type === "inpatient" && <BedSection {...sectionProps} />}
      <PrescriptionsSection {...sectionProps} />
    </div>
  );
}
