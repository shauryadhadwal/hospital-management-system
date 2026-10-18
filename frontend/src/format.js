// Small helpers that turn the raw values from the backend into text for the screen.
// The backend sends dates as text such as "2026-10-22T10:00:00" and money as text such as "8000.00".

// new Date(text) makes a JavaScript date from that text.
// toLocaleString() then writes it in the browser's language and time zone, e.g. "22/10/2026, 10:00:00".
export function formatDateTime(value) {
  if (!value) return ""; // "!value" is true for null, undefined and "" (nothing to show)
  return new Date(value).toLocaleString();
}

// Same idea, but only the date part, e.g. "22/10/2026".
export function formatDate(value) {
  if (!value) return "";
  return new Date(value).toLocaleDateString();
}

// Money: the backend sends Decimal values as text ("8000.00").
// Number(...) turns the text into a number, and toFixed(2) always writes two decimal places.
export function formatMoney(value) {
  return "₹" + Number(value).toFixed(2);
}
