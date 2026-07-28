import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { App } from "./App";
// Order matters: admin.css narrows a few rules from global.css (a button that must not be full
// width, for one), and both are single-class selectors -- so the later import has to be this one.
import "./styles/global.css";
import "./styles/admin.css";

const container = document.getElementById("root");
if (!container) throw new Error("#root is missing from index.html");

createRoot(container).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
