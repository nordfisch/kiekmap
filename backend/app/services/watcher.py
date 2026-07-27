"""Ueberwachung des Eingangsordners.

Was hier hineinkopiert wird, landet in der Datenbank -- ohne Anmeldung, ohne Oberflaeche. Fuer das
Museumsteam ist das der bequemste Weg, einen ganzen Stapel Scans einzuspielen.

**Warum abgefragt statt auf Ereignisse gehorcht:** Ein Dateiereignis kommt, sobald die Datei
angelegt wird -- nicht, wenn sie fertig geschrieben ist. Ein 80-MB-TIFF, ueber das Netz kopiert,
wuerde also halb importiert. Dazu kaemen Dateien, die waehrend eines Neustarts hineingelegt wurden
und deren Ereignis niemand gehoert hat. Ein Durchlauf alle paar Sekunden, der nur Dateien anfasst,
deren Groesse sich seit dem letzten Blick nicht geaendert hat, loest beides auf einmal -- und kostet
auf einem Pi fuer ein Verzeichnis nichts.
"""

import logging
import threading
from pathlib import Path

from app.config import Settings, get_settings
from app.db import SessionLocal
from app.services.importer import SONDERORDNER, importiere_datei

log = logging.getLogger(__name__)

#: Wie oft nachgesehen wird.
INTERVALL_S = 5.0


class Eingangswaechter:
    def __init__(self, settings: Settings | None = None, intervall: float = INTERVALL_S) -> None:
        self.settings = settings or get_settings()
        self.intervall = intervall
        self._stopp = threading.Event()
        self._thread: threading.Thread | None = None
        #: Dateigroesse beim letzten Durchlauf. Erst wenn sie sich nicht mehr aendert, ist die
        #: Datei fertig geschrieben.
        self._groessen: dict[Path, int] = {}

    # --- Betrieb ------------------------------------------------------------

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stopp.clear()
        self._thread = threading.Thread(target=self._schleife, name="eingang", daemon=True)
        self._thread.start()
        log.info("Eingangsordner wird ueberwacht: %s", self.settings.incoming_dir)

    def stop(self, timeout: float = 10.0) -> None:
        self._stopp.set()
        if self._thread:
            self._thread.join(timeout=timeout)
            self._thread = None

    def _schleife(self) -> None:
        while not self._stopp.is_set():
            try:
                self.durchlauf()
            except Exception:  # noqa: BLE001 -- der Waechter darf nie aufgeben
                log.exception("Fehler beim Durchsehen des Eingangsordners")
            self._stopp.wait(self.intervall)

    # --- Ein Durchlauf ------------------------------------------------------

    def _kandidaten(self) -> list[Path]:
        eingang = self.settings.incoming_dir
        if not eingang.is_dir():
            return []
        return [
            pfad
            for pfad in sorted(eingang.rglob("*"))
            if pfad.is_file()
            and not pfad.name.startswith(".")
            and not SONDERORDNER & set(pfad.relative_to(eingang).parts)
        ]

    def durchlauf(self) -> int:
        """Importiert, was fertig geschrieben ist. Gibt die Anzahl zurueck."""
        gesehen: dict[Path, int] = {}
        fertig: list[Path] = []

        for pfad in self._kandidaten():
            try:
                groesse = pfad.stat().st_size
            except OSError:
                continue  # zwischenzeitlich verschwunden
            gesehen[pfad] = groesse
            # Groesse unveraendert seit dem letzten Blick -- und nicht null, denn eine gerade erst
            # angelegte Datei ist zunaechst leer.
            if groesse > 0 and self._groessen.get(pfad) == groesse:
                fertig.append(pfad)

        self._groessen = gesehen

        if not fertig:
            return 0

        anzahl = 0
        with SessionLocal() as session:
            for pfad in fertig:
                ergebnis = importiere_datei(session, pfad, self.settings, beiseiteraeumen=True)
                self._groessen.pop(pfad, None)
                log.info("%s: %s -- %s", ergebnis.result, pfad.name, ergebnis.message)
                if ergebnis.erfolgreich:
                    anzahl += 1
            session.commit()

        return anzahl
