// Consumables: the nurse or doctor records the items used in this visit (gloves, dressings and so on).
// An item can be linked to one of this visit's procedures. The link is optional.

import { useEffect, useState } from "react";
import { apiGet, apiPost } from "../../api.js";
import { formatDateTime } from "../../format.js";

const EMPTY_USAGE = { consumable_id: "", quantity: "", procedure_history_id: "" };

export default function ConsumablesSection({ visit, staff, names, onChange }) {
  const [rows, setRows] = useState([]); // this visit's consumable usage
  const [history, setHistory] = useState([]); // this visit's procedure records (for the dropdown and labels)
  const [consumables, setConsumables] = useState([]); // the consumable list
  const [procedures, setProcedures] = useState([]); // the procedure list (to get a procedure's name)
  const [form, setForm] = useState(EMPTY_USAGE);
  const [error, setError] = useState("");

  // The catalogues are loaded once. Promise.all runs both requests together and waits for both.
  useEffect(() => {
    Promise.all([apiGet("/consumables"), apiGet("/procedures")])
      .then(([consumableRows, procedureRows]) => {
        setConsumables(consumableRows);
        setProcedures(procedureRows);
      })
      .catch((err) => setError(err.message));
  }, []);

  // This visit's usage and procedure records are loaded again each time the visit is reloaded.
  useEffect(() => {
    Promise.all([apiGet("/consumable-usage?visit_id=" + visit.id), apiGet("/procedure-history?visit_id=" + visit.id)])
      .then(([usageRows, historyRows]) => {
        setRows(usageRows);
        setHistory(historyRows);
      })
      .catch((err) => setError(err.message));
  }, [visit]);

  // Name of a consumable from its id.
  function consumableName(id) {
    const consumable = consumables.find((c) => c.id === id);
    return consumable ? consumable.name : "";
  }

  // Name of a procedure record: record -> procedure id -> procedure name.
  // "&&" stops early when a value is missing, so the next lookup is not run on nothing.
  function procedureLabel(historyId) {
    const record = history.find((h) => h.id === historyId);
    const procedure = record && procedures.find((p) => p.id === record.procedure_id);
    return procedure ? procedure.name : "-";
  }

  // The nurse and the doctor can record usage, while the visit is in progress.
  const canWrite = visit.status === "in progress" && ["nurse", "doctor"].includes(staff.role);

  async function save(event) {
    event.preventDefault();
    setError("");
    try {
      await apiPost("/consumable-usage", {
        visit_id: visit.id,
        consumable_id: Number(form.consumable_id),
        quantity: Number(form.quantity),
        // A blank box means "not linked to a procedure", which is sent as null.
        // "a ? b : c" is the same as "if a: b else c" in Python.
        procedure_history_id: form.procedure_history_id ? Number(form.procedure_history_id) : null,
      });
      setForm(EMPTY_USAGE);
      onChange();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="card">
      <h2>Consumables</h2>
      <table className="table">
        <thead>
          <tr>
            <th>Item</th>
            <th>Quantity</th>
            <th>Used at</th>
            <th>Recorded by</th>
            <th>Linked procedure</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id}>
              <td>{consumableName(r.consumable_id)}</td>
              <td>{r.quantity}</td>
              <td>{formatDateTime(r.used_at)}</td>
              {/* recorded_by is a staff id. */}
              <td>{names.staff[r.recorded_by]}</td>
              <td>{r.procedure_history_id ? procedureLabel(r.procedure_history_id) : "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {canWrite && (
        <form className="row" onSubmit={save}>
          {/* Each input is controlled: its value comes from form, and onChange copies the new value into form. */}
          <label>
            Item
            <select
              required
              value={form.consumable_id}
              onChange={(e) => setForm({ ...form, consumable_id: e.target.value })}
            >
              <option value="">Choose…</option>
              {consumables.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name} ({c.unit})
                </option>
              ))}
            </select>
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
          <label>
            Linked procedure (optional)
            <select
              value={form.procedure_history_id}
              onChange={(e) => setForm({ ...form, procedure_history_id: e.target.value })}
            >
              {/* The first option has value "" and means "no procedure". */}
              <option value="">None</option>
              {history.map((h) => (
                <option key={h.id} value={h.id}>
                  {procedureLabel(h.id)} ({formatDateTime(h.performed_at)})
                </option>
              ))}
            </select>
          </label>
          <button type="submit">Record usage</button>
        </form>
      )}
      {error && <p className="error">{error}</p>}
    </div>
  );
}
