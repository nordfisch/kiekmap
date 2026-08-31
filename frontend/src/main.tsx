import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { App } from "./App";
import { ErrorBoundary } from "./ErrorBoundary";
import { setLanguage, t } from "./text";
import type { Language } from "./text";
// Order matters: admin.css narrows a few rules from global.css (a button that must not be full
// width, for one), and both are single-class selectors -- so the later import has to be this one.
import "./styles/global.css";
import "./styles/admin.css";

const container = document.getElementById("root");
if (!container) throw new Error("#root is missing from index.html");

/**
 * The language of this device, from the backend.
 *
 * Not a Vite variable: that would need one build per language, and the point of the setting is
 * that a Pi is switched over by editing the `.env`. The kiosk service already waits for `/health`
 * before starting Chromium, so the backend answers by the time this runs.
 *
 * German if the call fails. A device whose backend is not up shows an error page anyway -- and a
 * wrong language is a smaller failure than a blank screen.
 */
async function language(): Promise<Language> {
  try {
    const response = await fetch("/api/config");
    if (!response.ok) return "de";
    const config = (await response.json()) as { language?: string };
    return config.language === "en" ? "en" : "de";
  } catch {
    return "de";
  }
}

/**
 * The language is resolved before the first render, so no component ever sees the wrong
 * catalogue.
 *
 * A function rather than a top-level `await`: that would raise the build target for the whole
 * bundle, and the browser this has to run in is the Chromium on the Pi.
 */
async function start(): Promise<void> {
  setLanguage(await language());
  document.documentElement.lang = t.locale.slice(0, 2);
  document.title = t.app.documentTitle;

  createRoot(container!).render(
    <StrictMode>
      {/* Around App, not inside it: a boundary only catches what is *below* it, so anything it
          is meant to survive has to be its child -- App included. */}
      <ErrorBoundary>
        <App />
      </ErrorBoundary>
    </StrictMode>,
  );
}

void start();
