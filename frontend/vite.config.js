// Settings for Vite, the tool that runs our development server on http://localhost:5173.

import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  // The React plugin lets Vite understand JSX (the HTML-like syntax inside .jsx files).
  plugins: [react()],

  server: {
    port: 5173,
    // The proxy forwards any request whose path starts with /api to the FastAPI backend.
    // Example: the browser asks for /api/auth/me, and Vite fetches http://localhost:8000/auth/me.
    // The browser only ever talks to localhost:5173, so the backend needs no CORS settings.
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        rewrite: (path) => path.replace(/^\/api/, ""), // strip the /api prefix
      },
    },
  },
});
