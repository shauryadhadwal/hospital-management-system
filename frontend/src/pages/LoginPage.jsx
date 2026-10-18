// The login form. On success it tells App who logged in, through the onLogin prop.

import { useState } from "react";
import { apiGet, login } from "../api.js";

// { onLogin } pulls the onLogin prop out of the props object App passed in.
export default function LoginPage({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  // Runs when the form is submitted (the button is clicked, or Enter is pressed).
  async function handleSubmit(event) {
    event.preventDefault(); // stop the browser's default behaviour of reloading the page
    setError("");
    // try/catch: if anything inside "try" throws an error, jump to "catch" instead of crashing.
    try {
      await login(username, password);
      const me = await apiGet("/auth/me");
      onLogin(me);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="login">
      <h1>Hospital login</h1>
      {/* onSubmit connects the form to our function. In JSX, "class" is written className. */}
      <form onSubmit={handleSubmit} className="form">
        <label>
          Username
          {/* A "controlled input": it shows the value from state, and every keystroke updates the state. */}
          <input value={username} onChange={(e) => setUsername(e.target.value)} />
        </label>
        <label>
          Password
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </label>
        <button type="submit">Log in</button>
        {/* "a && b" shows b only when a is truthy: the message appears only if there is an error. */}
        {error && <p className="error">{error}</p>}
      </form>
    </div>
  );
}
