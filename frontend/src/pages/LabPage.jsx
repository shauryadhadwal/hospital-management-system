// Lab orders page (lab role): the orders still waiting for a result, with a box to type the result.
// Saving a result completes the order, so it leaves this list. Completed orders are shown below.

import { useEffect, useState } from "react";
import { apiGet, apiPost } from "../api.js";
import { formatDateTime } from "../format.js";
import { loadNames } from "../names.js";

export default function LabPage() {
  const [orders, setOrders] = useState([]); // orders with status "ordered"
  const [completed, setCompleted] = useState([]); // orders with status "completed"
  const [results, setResults] = useState([]); // every lab result, to find the text of a completed order
  const [visits, setVisits] = useState([]); // needed to get from an order to its patient (order -> visit -> patient)
  const [tests, setTests] = useState([]); // the lab test list, for the test names
  const [names, setNames] = useState({ patients: {}, doctors: {}, staff: {} });
  // The text typed in each order's box. One object holds them all, keyed by the order id:
  // { 3: "Normal", 4: "High" }.
  const [texts, setTexts] = useState({});
  const [error, setError] = useState("");

  // Loads everything the page shows. Promise.all runs the requests together and waits for all of them.
  // The square brackets on the left unpack the results in the same order as the requests.
  async function loadAll() {
    try {
      const [orderRows, doneRows, resultRows, visitRows, testRows] = await Promise.all([
        apiGet("/lab-orders?status=ordered"),
        apiGet("/lab-orders?status=completed"),
        apiGet("/lab-results"),
        apiGet("/visits"),
        apiGet("/lab-tests"),
      ]);
      setOrders(orderRows);
      setCompleted(doneRows);
      setResults(resultRows);
      setVisits(visitRows);
      setTests(testRows);
    } catch (err) {
      setError(err.message);
    }
  }

  // Runs once when the page opens.
  useEffect(() => {
    loadAll();
    loadNames()
      .then(setNames)
      .catch((err) => setError(err.message));
  }, []);

  // Patient name for an order: find the order's visit, then read that visit's patient_id from the names lookup.
  function patientName(order) {
    const visit = visits.find((v) => v.id === order.visit_id);
    return visit ? names.patients[visit.patient_id] : "";
  }

  function testName(id) {
    const test = tests.find((t) => t.id === id);
    return test ? test.name : "";
  }

  function resultText(orderId) {
    const result = results.find((r) => r.lab_order_id === orderId);
    return result ? result.result_text : "";
  }

  // Saves the typed result for one order. "event" is the form submit; "order" is the row's order.
  async function saveResult(event, order) {
    event.preventDefault();
    setError("");
    try {
      await apiPost("/lab-results", { lab_order_id: order.id, result_text: texts[order.id] });
      loadAll(); // the order is now completed, so reload the lists
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div>
      <h1>Lab orders</h1>
      {error && <p className="error">{error}</p>}

      <div className="card">
        <h2>Waiting for a result</h2>
        {orders.length === 0 && <p className="muted">No orders are waiting.</p>}
        <table className="table">
          <thead>
            <tr>
              <th>Order</th>
              <th>Patient</th>
              <th>Test</th>
              <th>Ordered by</th>
              <th>Ordered at</th>
              <th>Result</th>
            </tr>
          </thead>
          <tbody>
            {orders.map((o) => (
              <tr key={o.id}>
                <td>{o.id}</td>
                <td>{patientName(o)}</td>
                <td>{testName(o.lab_test_id)}</td>
                {/* ordered_by is a doctor id. */}
                <td>{names.doctors[o.ordered_by]}</td>
                <td>{formatDateTime(o.ordered_at)}</td>
                <td>
                  {/* One small form per row. "required" stops an empty result being sent.
                      The text box is controlled: its value comes from texts[o.id].
                      { ...texts, [o.id]: value } copies all the old entries, then sets this one key.
                      [o.id] in square brackets means "use the number in o.id as the key name". */}
                  <form onSubmit={(e) => saveResult(e, o)}>
                    <textarea
                      required
                      rows="2"
                      value={texts[o.id] || ""}
                      onChange={(e) => setTexts({ ...texts, [o.id]: e.target.value })}
                    />
                    <button type="submit">Save result</button>
                  </form>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card">
        <h2>Completed</h2>
        <table className="table">
          <thead>
            <tr>
              <th>Order</th>
              <th>Patient</th>
              <th>Test</th>
              <th>Result</th>
            </tr>
          </thead>
          <tbody>
            {completed.map((o) => (
              <tr key={o.id}>
                <td>{o.id}</td>
                <td>{patientName(o)}</td>
                <td>{testName(o.lab_test_id)}</td>
                <td>{resultText(o.id)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
