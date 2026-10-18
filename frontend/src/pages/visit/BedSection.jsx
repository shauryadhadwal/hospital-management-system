// Bed stay (only for inpatient visits): the receptionist or nurse admits the patient to a bed,
// or moves them to another bed. VisitPage only shows this section when visit_type is "inpatient".

import { useEffect, useState } from "react";
import { apiGet, apiPost } from "../../api.js";
import { formatDateTime } from "../../format.js";

export default function BedSection({ visit, staff, onChange }) {
  const [stays, setStays] = useState([]); // this visit's bed stays, oldest first
  const [beds, setBeds] = useState([]); // every bed, room and ward: needed to write the bed names
  const [rooms, setRooms] = useState([]);
  const [wards, setWards] = useState([]);
  const [freeBeds, setFreeBeds] = useState([]); // beds nobody is in right now (for the dropdown)
  const [bedId, setBedId] = useState("");
  const [error, setError] = useState("");

  // The bed, room and ward lists are loaded once. Promise.all runs the three requests together.
  useEffect(() => {
    Promise.all([apiGet("/beds"), apiGet("/rooms"), apiGet("/wards")])
      .then(([bedRows, roomRows, wardRows]) => {
        setBeds(bedRows);
        setRooms(roomRows);
        setWards(wardRows);
      })
      .catch((err) => setError(err.message));
  }, []);

  // The stays and the free beds are loaded again each time the visit is reloaded.
  useEffect(() => {
    Promise.all([apiGet("/bed-assignments?visit_id=" + visit.id), apiGet("/beds/free")])
      .then(([stayRows, freeRows]) => {
        setStays(stayRows);
        setFreeBeds(freeRows);
      })
      .catch((err) => setError(err.message));
  }, [visit]);

  // Writes "Ward / room 101 / bed A" for a bed id.
  // The bed knows its room (room_id), and the room knows its ward (ward_id).
  // "a && b" stops early when a is missing, so the next lookup never runs on nothing.
  function bedLabel(id) {
    const bed = beds.find((b) => b.id === id);
    const room = bed && rooms.find((r) => r.id === bed.room_id);
    const ward = room && wards.find((w) => w.id === room.ward_id);
    if (!ward) return "";
    return `${ward.name} / room ${room.room_number} / bed ${bed.bed_number}`;
  }

  // An open stay has no end time yet: this is the bed the patient is in now.
  // .find returns the first stay that matches, or undefined if the patient is not in a bed.
  const openStay = stays.find((s) => !s.end_time);

  // The receptionist and the nurse can move patients, while the visit is in progress.
  const canWrite = visit.status === "in progress" && ["receptionist", "nurse"].includes(staff.role);

  async function save(event) {
    event.preventDefault();
    setError("");
    try {
      // If the patient is already in a bed, the move is a transfer. Otherwise it is a first admission.
      if (openStay) {
        await apiPost("/bed-assignments/" + openStay.id + "/transfer", { bed_id: Number(bedId) });
      } else {
        await apiPost("/bed-assignments", { visit_id: visit.id, bed_id: Number(bedId) });
      }
      setBedId("");
      onChange();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="card">
      <h2>Bed stay</h2>
      <table className="table">
        <thead>
          <tr>
            <th>Bed</th>
            <th>Start</th>
            <th>End</th>
          </tr>
        </thead>
        <tbody>
          {stays.map((s) => (
            <tr key={s.id}>
              <td>{bedLabel(s.bed_id)}</td>
              <td>{formatDateTime(s.start_time)}</td>
              <td>{s.end_time ? formatDateTime(s.end_time) : "current"}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {canWrite && (
        <form className="row" onSubmit={save}>
          <label>
            {openStay ? "Move to bed" : "Admit to bed"}
            <select required value={bedId} onChange={(e) => setBedId(e.target.value)}>
              <option value="">Choose…</option>
              {freeBeds.map((b) => (
                <option key={b.id} value={b.id}>
                  {`${b.ward_name} / room ${b.room_number} / bed ${b.bed_number} (${b.room_type}, ${b.daily_rate}/day)`}
                </option>
              ))}
            </select>
          </label>
          <button type="submit">{openStay ? "Transfer" : "Admit"}</button>
        </form>
      )}
      {error && <p className="error">{error}</p>}
    </div>
  );
}
