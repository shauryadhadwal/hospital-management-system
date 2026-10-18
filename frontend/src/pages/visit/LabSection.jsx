// Lab orders: the doctor orders a lab test for this visit. The result is entered later on the Lab orders page.

import { useEffect, useState } from "react";
import { apiGet, apiPost } from "../../api.js";
import { formatDateTime } from "../../format.js";

export default function LabSection({ visit, staff, onChange }) {
  const [orders, setOrders] = useState([]); // this visit's lab orders
  const [resultTexts, setResultTexts] = useState({}); // { order id: result text }, for orders that have a result
  const [tests, setTests] = useState([]); // the lab test list, for the dropdown and the test names
  const [testId, setTestId] = useState(""); // the dropdown's current choice
  const [error, setError] = useState("");

  // The test list does not change during a visit, so it is loaded once when the section appears.
  useEffect(() => {
    apiGet("/lab-tests")
      .then(setTests)
      .catch((err) => setError(err.message));
  }, []);

  // The orders are loaded again each time the visit is reloaded.
  useEffect(() => {
    loadOrders();
  }, [visit]);

  // Loads the orders and, for each one, its result (if the lab has written one).
  async function loadOrders() {
    try {
      const orderRows = await apiGet("/lab-orders?visit_id=" + visit.id);
      // Promise.all sends one results request per order at the same time, then waits for all of them.
      // The answers come back in the same order as orderRows.
      const resultLists = await Promise.all(orderRows.map((o) => apiGet("/lab-results?lab_order_id=" + o.id)));
      // Build the lookup { order id: result text }. An order has at most one result.
      // forEach runs the function once per item; "i" is the item's position (0, 1, 2...) in the list.
      const texts = {};
      orderRows.forEach((o, i) => {
        if (resultLists[i].length > 0) texts[o.id] = resultLists[i][0].result_text;
      });
      setOrders(orderRows);
      setResultTexts(texts);
    } catch (err) {
      setError(err.message);
    }
  }

  // .find returns the first test whose id matches, or undefined if none does.
  function testName(id) {
    const test = tests.find((t) => t.id === id);
    return test ? test.name : "";
  }

  // Only the doctor orders tests, and only while the visit is in progress.
  const canWrite = visit.status === "in progress" && staff.role === "doctor";

  async function orderTest(event) {
    event.preventDefault();
    setError("");
    try {
      await apiPost("/lab-orders", { visit_id: visit.id, lab_test_id: Number(testId) });
      setTestId("");
      onChange(); // reload the visit; this section then loads the new order
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="card">
      <h2>Lab orders</h2>
      <table className="table">
        <thead>
          <tr>
            <th>Test</th>
            <th>Ordered at</th>
            <th>Status</th>
            <th>Result</th>
          </tr>
        </thead>
        <tbody>
          {orders.map((o) => (
            <tr key={o.id}>
              <td>{testName(o.lab_test_id)}</td>
              <td>{formatDateTime(o.ordered_at)}</td>
              {/* The badge class is the status itself ("ordered", "completed"), so styles.css colours it. */}
              <td>
                <span className={"badge " + o.status}>{o.status}</span>
              </td>
              {/* "||" shows "-" when there is no result yet. */}
              <td>{resultTexts[o.id] || "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {canWrite && (
        <form className="row" onSubmit={orderTest}>
          <label>
            Lab test
            <select required value={testId} onChange={(e) => setTestId(e.target.value)}>
              <option value="">Choose…</option>
              {tests.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name}
                </option>
              ))}
            </select>
          </label>
          <button type="submit">Order test</button>
        </form>
      )}
      {error && <p className="error">{error}</p>}
    </div>
  );
}
