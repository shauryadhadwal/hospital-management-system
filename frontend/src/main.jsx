// Entry point: the first JavaScript file the browser runs (index.html loads it).
// It finds <div id="root"> and tells React to draw our App inside it.

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App.jsx";
import "./styles.css"; // importing a CSS file applies its styles to the whole page

createRoot(document.getElementById("root")).render(
  // StrictMode adds extra warnings during development; it does not change what you see.
  // BrowserRouter watches the URL in the address bar so <Routes> in App can pick a page.
  <StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>
);
