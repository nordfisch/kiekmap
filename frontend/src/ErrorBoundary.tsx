/**
 * The last net under the whole interface.
 *
 * React tears the entire tree down on a render error, and what is left is a white screen. In a
 * browser that is an annoyance -- somebody presses reload. Here there is nothing to press: the Pi
 * runs Chromium under `cage` with no keyboard, no address bar and no reload button, and the idle
 * reload that heals every other stuck state sits inside `MapView` and goes down with it.
 *
 * So this catches, says in German what happened, and reloads the page itself. Whether it may do
 * that a second time is decided in `recover.ts` -- a crash that returns on load must not turn the
 * screen into a strobe.
 */

import { Component, type ErrorInfo, type ReactNode } from "react";

import { RELOAD_DELAY_MS, lastRecovery, mayReload, noteRecovery } from "./recover";
import { t } from "./text";

type Props = { children: ReactNode };
type State = { failed: boolean; reloading: boolean };

export class ErrorBoundary extends Component<Props, State> {
  state: State = { failed: false, reloading: false };

  static getDerivedStateFromError(): Partial<State> {
    return { failed: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    // Nobody reads a console on the Pi. It is written for the one case that counts: somebody
    // reproducing the crash on a development machine.
    console.error("Kiekmap ist abgestuerzt:", error, info.componentStack);

    const now = Date.now();
    if (!mayReload(lastRecovery(sessionStorage), now)) return;

    // Noted before the reload rather than after: after it, this code no longer exists.
    noteRecovery(sessionStorage, now);
    this.setState({ reloading: true });

    // **The timer is deliberately never cleared, and there is no ``componentWillUnmount``.**
    //
    // The tidy version had one, and it made the whole thing do nothing: after catching, React
    // rebuilds the tree from scratch and takes this component with it -- measured on 19 August
    // 2026, the trace read "Timer gesetzt" and "unmount" one after the other, and the page stood
    // there unchanged. The cleanup reflex is right for a timer belonging to a view; it is wrong
    // for one belonging to the device.
    //
    // What it costs: a crash that the rebuild happens to fix still reloads eight seconds later.
    // For a kiosk that is the honest outcome anyway -- after a crash, a clean page.
    setTimeout(() => window.location.reload(), RELOAD_DELAY_MS);
  }

  render(): ReactNode {
    if (!this.state.failed) return this.props.children;

    return (
      <div className="splash">
        <div className="splash__panel">
          <p className="splash__title">{t.app.crashTitle}</p>
          <p>{this.state.reloading ? t.app.crashReloading : t.app.crashStuck}</p>
          {/* Always there, even while the timer runs: waiting eight seconds in front of a screen
              is long, and a finger is faster than any countdown. */}
          <button
            type="button"
            className="button button--primary"
            onClick={() => window.location.reload()}
          >
            {t.app.crashRetry}
          </button>
        </div>
      </div>
    );
  }
}
