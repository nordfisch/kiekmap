# Betriebshandbuch

> Wird in **Stufe 10 (Kiosk-Deployment)** gefüllt. Diese Datei ist der Ort für alles, was jemand
> wissen muss, der das Gerät im Museum am Laufen hält.

Geplanter Inhalt:

- Einrichtung eines neuen Pi von Grund auf (`deploy/pi/setup-pi.sh`)
- Was beim Einschalten passiert und woran man erkennt, dass etwas hakt
- Wartungsausgang: SSH, und die Tastenkombination, die vor Ort den Kiosk beendet
- Update ohne Internet: Stick anstecken, `update.sh`
- Sicherung auf USB und Wiederherstellung (die Bedienung steht in der
  [Kuratoren-Anleitung](kuratoren-anleitung.md), hier die Technik dahinter)
- SD-Karte klonen als Komplettsicherung des Geräts
- Fehlersuche: Container-Logs, Kiosk-Dienst, Display, Touch, USB-Automount

Schon jetzt gültig — **die PIN für den Admin-Bereich einrichten**:

```bash
cd backend && .venv/bin/python -m app.cli pin
```

Der Befehl fragt die PIN zweimal ab und gibt die Zeile aus, die in die `.env` gehört. Die PIN
selbst wird nirgends gespeichert; vergessen heißt neu setzen. Danach den Dienst neu starten.

Ist keine PIN eingerichtet, sagt das Zahlenfeld genau das — es lehnt nicht stumm jede Eingabe ab.
Nach fünf Fehlversuchen sperrt es für eine Minute. Die Sitzung endet nach 30 Minuten ohne
Bedienung; jede Aktion schiebt sie hinaus, und ein Neustart des Dienstes beendet jede Sitzung.

Das Gerät für einen anderen Ort einrichten: [adaption.md](adaption.md).
