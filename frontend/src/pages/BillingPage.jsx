// The billing list. It shows finished visits that still need an invoice, and all the invoices.

import { useEffect, useState } from "react";
// Link is a clickable link that changes the page without reloading the browser.
// useNavigate gives us a function that moves to another page after an action (like a redirect).
import { Link, useNavigate } from "react-router-dom";
import { apiGet, apiPost } from "../api.js";
import { formatDate, formatDateTime } from "../format.js";
import { loadNames } from "../names.js";

// { staff } is the logged-in person, passed in by App through a prop.
export default function BillingPage({ staff }) {
  const navigate = useNavigate();
  const isReceptionist = staff.role === "receptionist";

  // The lists we show. They start empty and are filled in by load().
  const [visits, setVisits] = useState([]);
  const [invoices, setInvoices] = useState([]);
  const [names, setNames] = useState({ patients: {}, doctors: {}, staff: {} });
  const [error, setError] = useState("");

  // Runs once when the page opens.
  useEffect(() => {
    load();
  }, []);

  async function load() {
    setError("");
    try {
      // Promise.all starts all three requests together and waits until every one has finished.
      // The results come back in the same order as the list we gave it.
      const [allVisits, allInvoices, nameLists] = await Promise.all([
        apiGet("/visits"),
        apiGet("/invoices"),
        loadNames(),
      ]);
      setVisits(allVisits);
      setInvoices(allInvoices);
      setNames(nameLists);
    } catch (err) {
      setError(err.message);
    }
  }

  // Creates an invoice for a finished visit, then opens its page.
  async function createInvoice(visit) {
    setError("");
    try {
      const created = await apiPost("/invoices", { visit_id: visit.id });
      navigate("/billing/" + created.id);
    } catch (err) {
      setError(err.message);
    }
  }

  // .filter builds a new list with only the items that pass the test.
  // Here: only the visits whose status is "completed".
  const completed = visits.filter((v) => v.status === "completed");

  // .some returns true if at least one item in the list passes the test.
  // Here: keep the completed visits where no invoice points at that visit yet.
  const readyToBill = completed.filter((v) => !invoices.some((inv) => inv.visit_id === v.id));

  // .find returns the first item that passes the test (or undefined if none does).
  // We use it to get the visit an invoice belongs to, so we can show the patient.
  function visitOf(invoice) {
    return visits.find((v) => v.id === invoice.visit_id);
  }

  return (
    <div className="page">
      <h1>Billing</h1>
      {error && <p className="error">{error}</p>}

      <div className="card">
        <h2>Ready to bill</h2>
        {/* <table> is an HTML table: rows (<tr>) made of header cells (<th>) and data cells (<td>). */}
        <table className="table">
          <thead>
            <tr>
              <th>Patient</th>
              <th>Doctor</th>
              <th>Discharged</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {/* .map turns each visit into one table row. The key tells React which row is which. */}
            {readyToBill.map((v) => (
              <tr key={v.id}>
                <td>{names.patients[v.patient_id]}</td>
                <td>{names.doctors[v.doctor_id]}</td>
                <td>{formatDateTime(v.actual_end)}</td>
                <td>
                  {isReceptionist && <button onClick={() => createInvoice(v)}>Create invoice</button>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {readyToBill.length === 0 && <p className="muted">No finished visits waiting for an invoice.</p>}
      </div>

      <div className="card">
        <h2>Invoices</h2>
        <table className="table">
          <thead>
            <tr>
              <th>Invoice</th>
              <th>Patient</th>
              <th>Date</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {invoices.map((inv) => {
              const visit = visitOf(inv);
              return (
                <tr key={inv.id}>
                  {/* Link turns into an <a> tag. "to" is the page it goes to: /billing/<invoice id>. */}
                  <td>
                    <Link to={"/billing/" + inv.id}>{inv.invoice_number}</Link>
                  </td>
                  <td>{visit && names.patients[visit.patient_id]}</td>
                  <td>{formatDate(inv.invoice_date)}</td>
                  <td>
                    {/* The class name "badge draft" (or issued, paid) gives the status its colour in styles.css. */}
                    <span className={"badge " + inv.status.replace(" ", "-")}>{inv.status}</span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        {invoices.length === 0 && <p className="muted">No invoices yet.</p>}
      </div>
    </div>
  );
}
