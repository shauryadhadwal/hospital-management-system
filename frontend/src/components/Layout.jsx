// The frame around every page after login: a header with the menu, the user's name and a logout button.

import { NavLink } from "react-router-dom";

// Which menu links each role sees. Each link is [URL, label].
// Admin setup (departments, staff, rooms, prices, insurance providers) is not in the menu:
// the admin does it in Swagger at /docs. Admin only views Patients, Visits and Billing here.
const MENU = {
  admin: [["/", "Home"], ["/patients", "Patients"], ["/visits", "Visits"], ["/billing", "Billing"]],
  receptionist: [["/", "Home"], ["/patients", "Patients"], ["/visits", "Visits"], ["/billing", "Billing"]],
  nurse: [["/", "Home"], ["/patients", "Patients"], ["/visits", "Visits"]],
  doctor: [["/", "Home"], ["/patients", "Patients"], ["/visits", "Visits"]],
  lab: [["/", "Home"], ["/lab", "Lab orders"]],
};

// "children" is a special prop: whatever is written between <Layout> and </Layout> in App.
export default function Layout({ staff, onLogout, children }) {
  const links = MENU[staff.role] || [];

  return (
    <div>
      <header className="header">
        <nav>
          {/* .map turns each [url, label] pair into a link. React needs a unique "key" for each item in a list. */}
          {links.map(([url, label]) => (
            // NavLink is a link that changes the URL without reloading the page,
            // and adds the "active" class when its URL is the current one.
            <NavLink key={url} to={url} end>
              {label}
            </NavLink>
          ))}
        </nav>
        <div>
          {staff.first_name} {staff.last_name} ({staff.role})
          <button onClick={onLogout}>Log out</button>
        </div>
      </header>
      <main className="page">{children}</main>
    </div>
  );
}
