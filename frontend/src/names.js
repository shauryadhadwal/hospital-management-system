// The backend lists only give ids (numbers) such as patient_id or doctor_id.
// This file loads the people lists and builds lookup objects, so a page can show "Dr. Rao" instead of "1".

import { apiGet } from "./api.js";

// "export async function" = a function other files can import, which can wait for the network with "await".
// It returns one object with three lookups, e.g. names.patients[3] is the name of patient 3.
export async function loadNames() {
  // Promise.all starts the three requests at the same time and waits until all of them have finished.
  // The results come back in the same order as the requests: [patients, doctors, staff].
  // The square brackets on the left are "destructuring": they unpack the array into three variables.
  const [patients, doctors, staff] = await Promise.all([
    apiGet("/patients"),
    apiGet("/doctors"),
    apiGet("/staff"),
  ]);

  // A plain object used as a lookup table: { 3: "Asha Rao", 4: "..." }.
  // .map turns each patient into a [id, name] pair, and Object.fromEntries turns those pairs into an object.
  const patientNames = Object.fromEntries(
    patients.map((p) => [p.id, `${p.first_name} ${p.last_name}`]) // backticks = text with ${...} inserted
  );
  const staffNames = Object.fromEntries(staff.map((s) => [s.id, `${s.first_name} ${s.last_name}`]));

  // A doctor row only has staff_id, so the doctor's name is found in the staff list.
  // .find returns the first item that matches the test, or undefined if none does.
  const doctorNames = {};
  for (const d of doctors) {
    const person = staff.find((s) => s.id === d.staff_id);
    doctorNames[d.id] = `Dr. ${person.first_name} ${person.last_name}`;
  }

  // JavaScript object keys are text, so names.patients[3] and names.patients["3"] are the same lookup.
  return { patients: patientNames, doctors: doctorNames, staff: staffNames };
}
