// One invoice: its lines, the charges that can still be added, insurance claims and payments.
// Each step is only shown when the invoice is in the right state (draft, issued or paid).

import { useEffect, useState } from "react";
// useParams reads the part of the URL marked with ":" in the route /billing/:id.
// For the address /billing/7 it gives { id: "7" }.
// Link is a clickable link that moves to another page without reloading the browser.
import { Link, useParams } from "react-router-dom";
import { apiDelete, apiGet, apiPost } from "../api.js";
import { formatDate, formatMoney } from "../format.js";
import { loadNames } from "../names.js";

// Turns a list of objects into a lookup table, so byId(list)[5] is the object whose id is 5.
// .map makes [id, item] pairs, and Object.fromEntries turns those pairs into one object.
function byId(list) {
  return Object.fromEntries(list.map((item) => [item.id, item]));
}

// { staff } is the logged-in person, passed in by App through a prop.
export default function InvoicePage({ staff }) {
  // Read the invoice id from the address bar.
  const { id } = useParams();
  const isReceptionist = staff.role === "receptionist";

  // data holds everything this page shows. It is null until the first load has finished.
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  // Form inputs. Each one is a piece of state, like the username box on the login page.
  const [claimPolicyId, setClaimPolicyId] = useState(""); // "" means "use the first policy"
  const [claimAmount, setClaimAmount] = useState("");
  const [paymentAmount, setPaymentAmount] = useState(null); // null means "use the balance"
  const [paymentMethod, setPaymentMethod] = useState("UPI");
  const [paymentReference, setPaymentReference] = useState("");
  const [other, setOther] = useState({ description: "", quantity: "1", unitPrice: "" });

  // Load the page when it opens, and again if the invoice id in the URL changes.
  useEffect(() => {
    load();
  }, [id]);

  // Fetches everything the page needs and stores it in data.
  async function load() {
    try {
      // Step 1: the invoice. We need its visit_id before we can ask for anything else.
      const invoice = await apiGet(`/invoices/${id}`);
      // Step 2: the visit. It tells us the patient, the doctor and the visit id for the sources.
      const visit = await apiGet(`/visits/${invoice.visit_id}`);
      // Step 3: everything else at the same time. Promise.all waits until all requests have finished.
      const [
        claims,
        payments,
        policies,
        providers,
        bedStays,
        labOrders,
        usages,
        beds,
        rooms,
        wards,
        labTests,
        consumables,
        procedureHistory,
        procedures,
        prescriptions,
        medications,
        doctor,
        names,
      ] = await Promise.all([
        apiGet(`/insurance-claims?invoice_id=${invoice.id}`),
        apiGet(`/payments?invoice_id=${invoice.id}`),
        apiGet(`/insurance-policies?patient_id=${visit.patient_id}`),
        apiGet("/insurance-providers"),
        apiGet(`/bed-assignments?visit_id=${visit.id}`),
        apiGet(`/lab-orders?visit_id=${visit.id}`),
        apiGet(`/consumable-usage?visit_id=${visit.id}`),
        apiGet("/beds"),
        apiGet("/rooms"),
        apiGet("/wards"),
        apiGet("/lab-tests"),
        apiGet("/consumables"),
        apiGet(`/procedure-history?visit_id=${visit.id}`),
        apiGet("/procedures"),
        apiGet(`/prescriptions?visit_id=${visit.id}`),
        apiGet("/medications"),
        apiGet(`/doctors/${visit.doctor_id}`),
        loadNames(),
      ]);
      setData({
        invoice,
        visit,
        claims,
        payments,
        policies,
        providers,
        bedStays,
        labOrders,
        usages,
        beds,
        rooms,
        wards,
        labTests,
        consumables,
        procedureHistory,
        procedures,
        prescriptions,
        medications,
        doctor,
        names,
      });
    } catch (err) {
      setError(err.message);
    }
  }

  // Every action goes through here. A function can be passed into another function (here: action),
  // which is like passing a Python function as an argument. We run the action, then reload the page.
  async function run(action) {
    setError("");
    try {
      await action();
      await load();
    } catch (err) {
      setError(err.message); // the backend's reason, for example "payment is more than the balance"
    }
  }

  // Locks the invoice: after this, lines can no longer be added or removed.
  function issueInvoice() {
    // window.confirm shows a yes/no box in the browser. It returns true if the user clicks OK.
    if (!window.confirm("Issue this invoice? Its lines cannot be changed after this.")) return;
    run(() => apiPost(`/invoices/${invoice.id}/issue`));
  }

  // Adds a free "other charge" line that is typed in by hand.
  async function addOtherCharge(event) {
    event.preventDefault();
    await run(async () => {
      await apiPost("/invoice-lines", {
        invoice_id: invoice.id,
        description: other.description,
        quantity: Number(other.quantity),
        unit_price: other.unitPrice,
      });
      setOther({ description: "", quantity: "1", unitPrice: "" });
    });
  }

  // Sends a new insurance claim for the amount typed in by the receptionist.
  async function submitClaim(event) {
    event.preventDefault();
    await run(async () => {
      await apiPost("/insurance-claims", {
        invoice_id: invoice.id,
        policy_id: Number(policyChoice),
        amount_claimed: claimAmount,
      });
      setClaimAmount("");
    });
  }

  // Records a payment from the patient.
  async function recordPayment(event) {
    event.preventDefault();
    await run(async () => {
      await apiPost("/payments", {
        invoice_id: invoice.id,
        amount: shownPayment,
        method: paymentMethod,
        reference: paymentReference || null, // "||" uses the right side when the left is empty
      });
      setPaymentAmount(null);
      setPaymentReference("");
    });
  }

  // Wait for the first load before drawing anything.
  if (!data) {
    return <div className="page">{error ? <p className="error">{error}</p> : <p>Loading…</p>}</div>;
  }

  // Pull the loaded pieces out of data so the rest of the page can use short names.
  const { invoice, visit, names, claims, payments, policies, providers } = data;

  // Lookup tables by id, for example beds[bed_id] gives the bed.
  const beds = byId(data.beds);
  const rooms = byId(data.rooms);
  const wards = byId(data.wards);
  const labTests = byId(data.labTests);
  const consumables = byId(data.consumables);
  const procedures = byId(data.procedures);
  const medications = byId(data.medications);
  const policyById = byId(policies);
  const providerById = byId(providers);

  // Who can do what on this page. Keeping these in one place makes the JSX below easier to read.
  const canEdit = isReceptionist && invoice.status === "draft"; // add or delete lines, issue
  const canClaim = isReceptionist && invoice.status === "issued"; // claims
  const canPay = isReceptionist && invoice.status === "issued" && Number(invoice.balance) > 0;

  // The policy shown in the claim form: the first one until the user picks another.
  const policyChoice = claimPolicyId || (policies.length ? String(policies[0].id) : "");
  // The amount shown in the payment form: the balance, unless the user has typed something.
  // "??" uses the right side when the left side is null.
  const shownPayment = paymentAmount ?? invoice.balance;

  // Builds a label such as "ICU room 101 bed 1" from a bed, its room and its ward.
  function bedLabel(bedId) {
    const bed = beds[bedId];
    const room = rooms[bed.room_id];
    const ward = wards[room.ward_id];
    return `${ward.name} room ${room.room_number} bed ${bed.bed_number}`;
  }

  // .some returns true if any line on the invoice matches. Used to hide charges already billed.
  function isBilled(sourceType, sourceId) {
    return invoice.lines.some((line) => line.source_type === sourceType && line.source_id === sourceId);
  }

  // A linked row: the backend fills in the description, quantity and price from the source itself.
  // So a linked charge cannot be billed twice and the price cannot be typed wrong.
  function linkedRow(sourceType, source, label) {
    return {
      key: sourceType + "-" + source.id,
      label,
      payload: { invoice_id: invoice.id, source_type: sourceType, source_id: source.id },
    };
  }

  // Linked charges: each bed stay, lab order and consumable usage of this visit that is not billed yet.
  // .filter keeps the unbilled ones and .map turns each one into a row.
  // The three dots (...) copy every item of one list into the list we are building.
  const linkedRows = [
    ...data.bedStays
      .filter((s) => !isBilled("bed_assignment", s.id))
      .map((s) => linkedRow("bed_assignment", s, "Bed stay: " + bedLabel(s.bed_id))),
    ...data.labOrders
      .filter((o) => !isBilled("lab_order", o.id))
      .map((o) => linkedRow("lab_order", o, "Lab test: " + labTests[o.lab_test_id].name)),
    ...data.usages
      .filter((u) => !isBilled("consumable_usage", u.id))
      .map((u) => linkedRow("consumable_usage", u, `Consumable: ${consumables[u.consumable_id].name} ×${u.quantity}`)),
  ];

  // Typed charges: the description, quantity and price are sent by the frontend.
  // Per docs/user_journey.md the price is copied from the price lists (doctor fee, procedure price,
  // medication price) and the quantity comes from the prescription.
  const typedCharges = [
    {
      description: "Consultation: " + names.doctors[visit.doctor_id],
      quantity: 1,
      unit_price: data.doctor.consultation_fee,
    },
    ...data.procedureHistory.map((row) => {
      const procedure = procedures[row.procedure_id];
      return { description: "Procedure: " + procedure.name, quantity: 1, unit_price: procedure.price };
    }),
    ...data.prescriptions.map((p) => {
      const medication = medications[p.medication_id];
      return {
        description: `Medication: ${medication.name} ${medication.strength}`,
        quantity: p.quantity,
        unit_price: medication.price,
      };
    }),
  ]
    // Hide a suggestion when a line with the same description is already on the invoice.
    .filter((c) => !invoice.lines.some((line) => line.description === c.description))
    .map((c, index) => ({
      key: "typed-" + index,
      label: c.description,
      payload: {
        invoice_id: invoice.id,
        description: c.description,
        quantity: c.quantity,
        unit_price: c.unit_price,
      },
    }));

  const suggestions = [...linkedRows, ...typedCharges];

  return (
    <div className="page">
      <Link to="/billing">Back to billing</Link>
      {error && <p className="error">{error}</p>}

      {/* Header card: who the invoice is for, and the totals. */}
      <div className="card">
        <h1>Invoice {invoice.invoice_number}</h1>
        <p>
          <span className={"badge " + invoice.status.replace(" ", "-")}>{invoice.status}</span>
        </p>
        <p>
          Patient: {names.patients[visit.patient_id]} · Doctor: {names.doctors[visit.doctor_id]} · Date:{" "}
          {formatDate(invoice.invoice_date)}
        </p>
        <div className="summary">
          <p>
            Total <strong>{formatMoney(invoice.total)}</strong>
          </p>
          <p>
            Paid by insurer <strong>{formatMoney(invoice.paid_claims)}</strong>
          </p>
          <p>
            Paid by patient <strong>{formatMoney(invoice.payments)}</strong>
          </p>
          <p>
            Balance <strong>{formatMoney(invoice.balance)}</strong>
          </p>
        </div>
      </div>

      {/* Lines table. Each line's amount is quantity times unit price. */}
      <div className="card">
        <h2>Lines</h2>
        <table className="table">
          <thead>
            <tr>
              <th>Description</th>
              <th>Qty</th>
              <th>Unit price</th>
              <th>Amount</th>
              {canEdit && <th></th>}
            </tr>
          </thead>
          <tbody>
            {invoice.lines.map((line) => (
              <tr key={line.id}>
                <td>{line.description}</td>
                <td>{line.quantity}</td>
                <td>{formatMoney(line.unit_price)}</td>
                {/* Number() turns the price text from the backend into a number so we can multiply. */}
                <td>{formatMoney((line.quantity * Number(line.unit_price)).toFixed(2))}</td>
                {canEdit && (
                  <td>
                    <button onClick={() => run(() => apiDelete(`/invoice-lines/${line.id}`))}>Delete</button>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
        {invoice.lines.length === 0 && <p className="muted">No lines yet.</p>}
        {canEdit && (
          <button onClick={issueInvoice} disabled={invoice.lines.length === 0}>
            Issue invoice
          </button>
        )}
      </div>

      {/* Charges that can still be added. Only while the invoice is a draft. */}
      {canEdit && (
        <div className="card">
          <h2>Charges to add</h2>
          {/* .map gives one list item per suggestion. "key" must be unique within the list. */}
          <ul>
            {suggestions.map((s) => (
              <li key={s.key}>
                {s.label} <button onClick={() => run(() => apiPost("/invoice-lines", s.payload))}>Add</button>
              </li>
            ))}
          </ul>
          {suggestions.length === 0 && <p className="muted">Nothing else to add.</p>}

          <h3>Other charge</h3>
          <form onSubmit={addOtherCharge} className="row">
            <label>
              Description
              {/* Each input is controlled: it shows the state, and typing updates it.
                  { ...other, description: ... } copies the old values and changes only one of them. */}
              <input
                value={other.description}
                onChange={(e) => setOther({ ...other, description: e.target.value })}
              />
            </label>
            <label>
              Quantity
              <input
                type="number"
                min="1"
                value={other.quantity}
                onChange={(e) => setOther({ ...other, quantity: e.target.value })}
              />
            </label>
            <label>
              Unit price
              <input
                value={other.unitPrice}
                onChange={(e) => setOther({ ...other, unitPrice: e.target.value })}
              />
            </label>
            <button type="submit">Add other charge</button>
          </form>
        </div>
      )}

      {/* Insurance claims. Shown once the invoice has been issued (or paid). */}
      {invoice.status !== "draft" && (
        <div className="card">
          <h2>Insurance claims</h2>
          <table className="table">
            <thead>
              <tr>
                <th>Policy</th>
                <th>Amount</th>
                <th>Status</th>
                <th>Submitted</th>
                <th>Approved</th>
                <th>Paid</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {claims.map((claim) => {
                const policy = policyById[claim.policy_id];
                return (
                  <tr key={claim.id}>
                    <td>
                      {policy.policy_number} ({providerById[policy.provider_id].name})
                    </td>
                    <td>{formatMoney(claim.amount_claimed)}</td>
                    <td>
                      <span className={"badge " + claim.status.replace(" ", "-")}>{claim.status}</span>
                    </td>
                    {/* The dates are empty until that step happens, so show "-" instead. */}
                    <td>{formatDate(claim.submitted_date)}</td>
                    <td>{claim.approved_date ? formatDate(claim.approved_date) : "-"}</td>
                    <td>{claim.paid_date ? formatDate(claim.paid_date) : "-"}</td>
                    <td>
                      {canClaim && claim.status === "submitted" && (
                        <button onClick={() => run(() => apiPost(`/insurance-claims/${claim.id}/approve`))}>
                          Approve
                        </button>
                      )}
                      {canClaim && claim.status === "approved" && (
                        <button onClick={() => run(() => apiPost(`/insurance-claims/${claim.id}/pay`))}>
                          Mark paid
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          {claims.length === 0 && <p className="muted">No insurance claims yet.</p>}

          {canClaim &&
            (policies.length === 0 ? (
              <p className="muted">This patient has no insurance policy.</p>
            ) : (
              <form onSubmit={submitClaim} className="row">
                <label>
                  Policy
                  {/* <select> is a drop-down list. Its <option> children are the choices.
                      The value is the policy id, which is what the backend needs. */}
                  <select value={policyChoice} onChange={(e) => setClaimPolicyId(e.target.value)}>
                    {policies.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.policy_number} ({providerById[p.provider_id].name})
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  Amount claimed
                  <input value={claimAmount} onChange={(e) => setClaimAmount(e.target.value)} />
                </label>
                <button type="submit">Submit claim</button>
              </form>
            ))}
          {canClaim && (
            <p className="muted">The claim amount is typed in by the receptionist. It is not worked out from the invoice.</p>
          )}
        </div>
      )}

      {/* Payments. The list is always shown; the form only while the invoice is issued and still owes money. */}
      <div className="card">
        <h2>Payments</h2>
        <table className="table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Amount</th>
              <th>Method</th>
              <th>Reference</th>
            </tr>
          </thead>
          <tbody>
            {payments.map((p) => (
              <tr key={p.id}>
                <td>{formatDate(p.paid_at)}</td>
                <td>{formatMoney(p.amount)}</td>
                <td>{p.method}</td>
                <td>{p.reference || "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {payments.length === 0 && <p className="muted">No payments yet.</p>}

        {canPay && (
          <form onSubmit={recordPayment} className="row">
            <label>
              Amount
              <input value={shownPayment} onChange={(e) => setPaymentAmount(e.target.value)} />
            </label>
            <label>
              Method
              <select value={paymentMethod} onChange={(e) => setPaymentMethod(e.target.value)}>
                {["cash", "card", "UPI", "bank transfer"].map((m) => (
                  <option key={m} value={m}>
                    {m}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Reference
              <input value={paymentReference} onChange={(e) => setPaymentReference(e.target.value)} />
            </label>
            <button type="submit">Record payment</button>
          </form>
        )}
      </div>
    </div>
  );
}
