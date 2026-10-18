// Patients: search for a patient, register a new one, and (for the receptionist) add an insurance policy
// and book a visit for the selected patient.

import { useEffect, useState } from "react";
import { Link } from "react-router-dom"; // Link is an <a> tag that changes the page without reloading it
import { apiGet, apiPost } from "../api.js";
import { formatDate, formatDateTime } from "../format.js";
import { loadNames } from "../names.js";

// The empty values for each form. A text box holds "" when it is empty.
const EMPTY_PATIENT = {
  first_name: "",
  last_name: "",
  age: "",
  sex: "male",
  phone: "",
  email: "",
  address: "",
  emergency_contact_name: "",
  emergency_contact_phone: "",
  emergency_contact_relationship: "",
};

const EMPTY_POLICY = { provider_id: "", policy_number: "", valid_from: "", valid_to: "" };

const EMPTY_VISIT = { doctor_id: "", visit_type: "outpatient", planned_start: "", chief_complaint: "" };

// The backend wants null for an optional field left blank, not "".
// This builds a new object with the same keys, where every "" becomes null.
function blankToNull(form) {
  const result = {};
  for (const key of Object.keys(form)) {
    result[key] = form[key] === "" ? null : form[key];
  }
  return result;
}

export default function PatientsPage({ staff }) {
  const [search, setSearch] = useState("");
  const [patients, setPatients] = useState([]); // the search results
  const [selected, setSelected] = useState(null); // the patient chosen with "Select", or null
  const [policies, setPolicies] = useState([]); // the selected patient's insurance policies
  const [visits, setVisits] = useState([]); // the selected patient's visits
  const [providers, setProviders] = useState([]); // insurance providers, for the dropdown and names
  const [doctors, setDoctors] = useState([]); // doctor rows: id and staff_id
  const [staffRows, setStaffRows] = useState([]); // staff rows: they hold each person's department_id
  const [names, setNames] = useState({ patients: {}, doctors: {}, staff: {} });
  const [patientForm, setPatientForm] = useState(EMPTY_PATIENT);
  const [policyForm, setPolicyForm] = useState(EMPTY_POLICY);
  const [visitForm, setVisitForm] = useState(EMPTY_VISIT);
  const [error, setError] = useState("");

  // useEffect with [] runs once, when the page opens: load the lists the forms need.
  useEffect(() => {
    // Promise.all starts all four requests at the same time and waits for all of them.
    // The results arrive in the same order as the requests, so the destructuring below
    // "unpacks" them into four named variables.
    Promise.all([loadNames(), apiGet("/doctors"), apiGet("/staff"), apiGet("/insurance-providers")])
      .then(([loadedNames, doctorRows, staffList, providerRows]) => {
        setNames(loadedNames);
        setDoctors(doctorRows);
        setStaffRows(staffList);
        setProviders(providerRows);
      })
      .catch((err) => setError(err.message));
    searchPatients(""); // show everybody to start with
  }, []);

  // Asks the backend for patients whose first or last name contains the text.
  async function searchPatients(name) {
    try {
      // An empty search means "all patients", so the ?name= part is only added when there is text.
      // encodeURIComponent makes the text safe for a URL (a space becomes %20).
      const query = name ? "?name=" + encodeURIComponent(name) : "";
      setPatients(await apiGet("/patients" + query));
    } catch (err) {
      setError(err.message);
    }
  }

  // Loads the selected patient's policies and visits.
  async function loadRecords(patientId) {
    try {
      const [policyRows, visitRows] = await Promise.all([
        apiGet("/insurance-policies?patient_id=" + patientId),
        apiGet("/visits?patient_id=" + patientId),
      ]);
      setPolicies(policyRows);
      setVisits(visitRows);
    } catch (err) {
      setError(err.message);
    }
  }

  // The second argument [selected] means: run this again whenever "selected" changes to a different patient.
  useEffect(() => {
    if (selected) loadRecords(selected.id);
  }, [selected]);

  // Runs when the search form is submitted (the Search button or Enter).
  function handleSearch(event) {
    event.preventDefault(); // stop the browser reloading the page
    setError("");
    searchPatients(search);
  }

  async function registerPatient(event) {
    event.preventDefault();
    setError("");
    try {
      // "{ ...object, age: 5 }" copies every field of the object, then sets age.
      // Here the copy comes from blankToNull and age is replaced by a real number.
      const created = await apiPost("/patients", {
        ...blankToNull(patientForm),
        age: Number(patientForm.age), // the box holds text such as "42"; the backend wants a number
      });
      setPatientForm(EMPTY_PATIENT);
      setSelected(created); // open the new patient straight away
      searchPatients(search);
    } catch (err) {
      setError(err.message);
    }
  }

  async function addPolicy(event) {
    event.preventDefault();
    setError("");
    try {
      await apiPost("/insurance-policies", {
        ...policyForm,
        patient_id: selected.id,
        provider_id: Number(policyForm.provider_id), // the dropdown gives text; the backend wants a number
      });
      setPolicyForm(EMPTY_POLICY);
      loadRecords(selected.id);
    } catch (err) {
      setError(err.message);
    }
  }

  async function bookVisit(event) {
    event.preventDefault();
    setError("");
    try {
      const doctorId = Number(visitForm.doctor_id);
      // A visit belongs to the doctor's department, so the department is taken from the doctor's staff row.
      // .find returns the first item that passes the test, here the doctor (or the staff row) with the matching id.
      const doctor = doctors.find((d) => d.id === doctorId);
      const doctorStaff = staffRows.find((s) => s.id === doctor.staff_id);
      await apiPost("/visits", {
        patient_id: selected.id,
        doctor_id: doctorId,
        department_id: doctorStaff.department_id,
        visit_type: visitForm.visit_type,
        // A datetime-local box gives text such as "2026-10-22T10:00", which the backend reads as a date and time.
        planned_start: visitForm.planned_start,
        // "a || b" means: a if it has a value, otherwise b. An empty complaint is sent as null.
        chief_complaint: visitForm.chief_complaint || null,
      });
      setVisitForm(EMPTY_VISIT);
      loadRecords(selected.id);
    } catch (err) {
      setError(err.message);
    }
  }

  // Finds a provider's name from its id. Returns "" if it is not in the list.
  function providerName(id) {
    const provider = providers.find((p) => p.id === id);
    return provider ? provider.name : "";
  }

  return (
    <div>
      <h1>Patients</h1>
      {error && <p className="error">{error}</p>}

      <div className="card">
        <h2>Find a patient</h2>
        <form className="row" onSubmit={handleSearch}>
          <label>
            Name
            <input value={search} onChange={(e) => setSearch(e.target.value)} />
          </label>
          <button type="submit">Search</button>
        </form>

        {/* A <table> shows rows and columns. <thead> is the header row, <tbody> holds the data rows,
            <tr> is one row, <th> is a header cell and <td> is a normal cell. */}
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Sex</th>
              <th>Date of birth</th>
              <th>Phone</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {/* .map turns each patient into one table row. "key" is a unique id React uses to track the row. */}
            {patients.map((p) => (
              <tr key={p.id}>
                <td>{p.id}</td>
                <td>
                  {p.first_name} {p.last_name}
                </td>
                <td>{p.sex}</td>
                <td>{formatDate(p.date_of_birth)}</td>
                <td>{p.phone}</td>
                <td>
                  {/* An arrow function "() => setSelected(p)" runs setSelected only when the button is clicked. */}
                  <button onClick={() => setSelected(p)}>Select</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Only the receptionist sees the register form. "a && b" shows b only when a is true. */}
      {staff.role === "receptionist" && (
        <div className="card">
          <h2>Register a new patient</h2>
          {/* "required" stops the browser sending the form while that box is empty.
              Each input is "controlled": its value comes from state, and every keystroke updates the state.
              { ...patientForm, first_name: e.target.value } copies the whole form, then changes one field. */}
          <form className="row" onSubmit={registerPatient}>
            <label>
              First name
              <input
                required
                value={patientForm.first_name}
                onChange={(e) => setPatientForm({ ...patientForm, first_name: e.target.value })}
              />
            </label>
            <label>
              Last name
              <input
                required
                value={patientForm.last_name}
                onChange={(e) => setPatientForm({ ...patientForm, last_name: e.target.value })}
              />
            </label>
            <label>
              Age
              {/* type="number" makes the browser accept digits only. */}
              <input
                type="number"
                required
                min="0"
                max="130"
                value={patientForm.age}
                onChange={(e) => setPatientForm({ ...patientForm, age: e.target.value })}
              />
            </label>
            <label>
              Sex
              {/* <select> is a dropdown. Each <option> is one choice: "value" is what gets saved, the text is what is shown. */}
              <select value={patientForm.sex} onChange={(e) => setPatientForm({ ...patientForm, sex: e.target.value })}>
                <option value="male">male</option>
                <option value="female">female</option>
                <option value="other">other</option>
              </select>
            </label>
            <label>
              Phone
              <input
                required
                value={patientForm.phone}
                onChange={(e) => setPatientForm({ ...patientForm, phone: e.target.value })}
              />
            </label>
            <label>
              Email
              <input value={patientForm.email} onChange={(e) => setPatientForm({ ...patientForm, email: e.target.value })} />
            </label>
            <label>
              Address
              <input
                value={patientForm.address}
                onChange={(e) => setPatientForm({ ...patientForm, address: e.target.value })}
              />
            </label>
            <label>
              Emergency contact name
              <input
                value={patientForm.emergency_contact_name}
                onChange={(e) => setPatientForm({ ...patientForm, emergency_contact_name: e.target.value })}
              />
            </label>
            <label>
              Emergency contact phone
              <input
                value={patientForm.emergency_contact_phone}
                onChange={(e) => setPatientForm({ ...patientForm, emergency_contact_phone: e.target.value })}
              />
            </label>
            <label>
              Relationship
              <input
                value={patientForm.emergency_contact_relationship}
                onChange={(e) => setPatientForm({ ...patientForm, emergency_contact_relationship: e.target.value })}
              />
            </label>
            <button type="submit">Register patient</button>
          </form>
        </div>
      )}

      {/* The selected patient's details. This only appears after "Select" has been clicked. */}
      {selected && (
        <div className="card">
          <h2>
            {selected.first_name} {selected.last_name} (patient {selected.id})
          </h2>
          <p>
            Date of birth: {formatDate(selected.date_of_birth)} · Sex: {selected.sex} · Phone: {selected.phone}
          </p>
          <p>
            Email: {selected.email || "-"} · Address: {selected.address || "-"}
          </p>
          <p>
            Emergency contact: {selected.emergency_contact_name || "-"}
            {selected.emergency_contact_relationship && ` (${selected.emergency_contact_relationship})`}
            {selected.emergency_contact_phone && `, ${selected.emergency_contact_phone}`}
          </p>

          <h3>Insurance policies</h3>
          <table className="table">
            <thead>
              <tr>
                <th>Provider</th>
                <th>Policy number</th>
                <th>Valid from</th>
                <th>Valid to</th>
              </tr>
            </thead>
            <tbody>
              {policies.map((pol) => (
                <tr key={pol.id}>
                  <td>{providerName(pol.provider_id)}</td>
                  <td>{pol.policy_number}</td>
                  <td>{formatDate(pol.valid_from)}</td>
                  <td>{formatDate(pol.valid_to)}</td>
                </tr>
              ))}
            </tbody>
          </table>

          {staff.role === "receptionist" && (
            <form className="row" onSubmit={addPolicy}>
              <label>
                Provider
                <select
                  required
                  value={policyForm.provider_id}
                  onChange={(e) => setPolicyForm({ ...policyForm, provider_id: e.target.value })}
                >
                  <option value="">Choose…</option>
                  {providers.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Policy number
                <input
                  required
                  value={policyForm.policy_number}
                  onChange={(e) => setPolicyForm({ ...policyForm, policy_number: e.target.value })}
                />
              </label>
              <label>
                Valid from
                {/* type="date" gives a calendar box; its value is text such as "2026-01-01". */}
                <input
                  type="date"
                  required
                  value={policyForm.valid_from}
                  onChange={(e) => setPolicyForm({ ...policyForm, valid_from: e.target.value })}
                />
              </label>
              <label>
                Valid to
                <input
                  type="date"
                  required
                  value={policyForm.valid_to}
                  onChange={(e) => setPolicyForm({ ...policyForm, valid_to: e.target.value })}
                />
              </label>
              <button type="submit">Add policy</button>
            </form>
          )}

          <h3>Visits</h3>
          <table className="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Doctor</th>
                <th>Type</th>
                <th>Status</th>
                <th>Planned start</th>
              </tr>
            </thead>
            <tbody>
              {visits.map((v) => (
                <tr key={v.id}>
                  {/* Link goes to the visit page, e.g. /visits/5. */}
                  <td>
                    <Link to={"/visits/" + v.id}>{v.id}</Link>
                  </td>
                  <td>{names.doctors[v.doctor_id]}</td>
                  <td>{v.visit_type}</td>
                  {/* status "in progress" becomes the badge class "in-progress" (see styles.css). */}
                  <td>
                    <span className={"badge " + v.status.replace(" ", "-")}>{v.status}</span>
                  </td>
                  <td>{formatDateTime(v.planned_start)}</td>
                </tr>
              ))}
            </tbody>
          </table>

          {staff.role === "receptionist" && (
            <form className="row" onSubmit={bookVisit}>
              <label>
                Doctor
                <select
                  required
                  value={visitForm.doctor_id}
                  onChange={(e) => setVisitForm({ ...visitForm, doctor_id: e.target.value })}
                >
                  <option value="">Choose…</option>
                  {doctors.map((d) => (
                    <option key={d.id} value={d.id}>
                      {names.doctors[d.id]}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Type
                <select
                  value={visitForm.visit_type}
                  onChange={(e) => setVisitForm({ ...visitForm, visit_type: e.target.value })}
                >
                  <option value="outpatient">outpatient</option>
                  <option value="inpatient">inpatient</option>
                </select>
              </label>
              <label>
                Planned start
                <input
                  type="datetime-local"
                  required
                  value={visitForm.planned_start}
                  onChange={(e) => setVisitForm({ ...visitForm, planned_start: e.target.value })}
                />
              </label>
              <label>
                Chief complaint
                <input
                  value={visitForm.chief_complaint}
                  onChange={(e) => setVisitForm({ ...visitForm, chief_complaint: e.target.value })}
                />
              </label>
              <button type="submit">Book visit</button>
            </form>
          )}
        </div>
      )}
    </div>
  );
}
