/**
 * The number pad.
 *
 * A PIN rather than a password because there is no keyboard in the museum -- and no on-screen
 * keyboard either, since Chromium in kiosk mode does not bring one. Keys of 4.5 rem, so they can
 * be hit standing, with the pad of a finger, by someone wearing reading glasses.
 */

import { useState } from "react";

import { useAdmin } from "../store/admin";
import { t } from "../text/de";

const MIN_LENGTH = 4;
const MAX_LENGTH = 12;
const KEYS = ["1", "2", "3", "4", "5", "6", "7", "8", "9"];

export function PinPad() {
  const signIn = useAdmin((s) => s.signIn);
  const cancel = useAdmin((s) => s.cancelPin);
  const busy = useAdmin((s) => s.busy);
  const error = useAdmin((s) => s.error);
  const [pin, setPin] = useState("");

  function press(digit: string) {
    setPin((current) => (current.length < MAX_LENGTH ? current + digit : current));
  }

  function submit() {
    if (pin.length < MIN_LENGTH || busy) return;
    void signIn(pin);
    // Emptied right away, not once an error arrives: on a second wrong attempt the message is the
    // same string, so watching it for a change would leave the old digits standing. Fishing for
    // the mistyped one in a row of dots is hopeless anyway.
    setPin("");
  }

  return (
    <div className="pinpad" role="dialog" aria-modal="true" aria-label={t.admin.pin.title}>
      <div className="pinpad__box">
        <h2 className="pinpad__title">{t.admin.pin.title}</h2>
        <p className="pinpad__hint">{t.admin.pin.hint}</p>

        <div className="pinpad__display" aria-live="polite" aria-label={`${pin.length}`}>
          {Array.from({ length: MAX_LENGTH }, (_, index) => (
            <span
              key={index}
              className={index < pin.length ? "pinpad__dot pinpad__dot--filled" : "pinpad__dot"}
              hidden={index >= Math.max(MIN_LENGTH, pin.length)}
            />
          ))}
        </div>

        {error && <p className="pinpad__error">{error}</p>}

        <div className="pinpad__keys">
          {KEYS.map((digit) => (
            <button
              key={digit}
              type="button"
              className="pinpad__key"
              onClick={() => press(digit)}
              disabled={busy}
            >
              {digit}
            </button>
          ))}
          <button
            type="button"
            className="pinpad__key pinpad__key--quiet"
            onClick={() => setPin((current) => current.slice(0, -1))}
            disabled={busy || pin.length === 0}
          >
            {t.admin.pin.delete}
          </button>
          <button type="button" className="pinpad__key" onClick={() => press("0")} disabled={busy}>
            0
          </button>
          <button
            type="button"
            className="pinpad__key pinpad__key--primary"
            onClick={submit}
            disabled={busy || pin.length < MIN_LENGTH}
          >
            {t.admin.pin.submit}
          </button>
        </div>

        <button type="button" className="button button--quiet" onClick={cancel}>
          {t.admin.pin.cancel}
        </button>
      </div>
    </div>
  );
}
