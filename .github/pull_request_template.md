<!-- Ziel ist `develop`, nicht `main`. Warum, steht in docs/development.md. -->

**Was ändert sich, und warum?**



**Woran hängt es?**

<!-- Issue, Meldung, oder nichts davon -- alles drei ist in Ordnung. -->

- Issue:

**Vor dem Absenden**

- [ ] `make check` ist grün — Stil, die fünf Prüfungen, alle Tests
- [ ] Die fachliche Entscheidung hat einen Test, der den **Fehlerfall** beschreibt, nicht nur den
      Erfolgsfall
- [ ] Nichts Ortsspezifisches im Code: keine Koordinate, kein Ortsname, keine sammlungsabhängige
      Zahl. Testdaten sind ausgenommen
- [ ] Keine Namen aus einem echten Bestand — auch nicht im Kommentar
- [ ] Bei einem erledigten Issue: CHANGELOG nachgezogen, Issue verlinkt
      (und `decisions.md`, falls eine Entscheidung herauskam)
