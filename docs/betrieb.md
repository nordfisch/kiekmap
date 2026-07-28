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

Das Gerät für einen anderen Ort einrichten: [adaption.md](adaption.md).
