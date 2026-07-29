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

---

## USB-Sticks sichtbar machen

> **Noch nicht auf einem Pi erprobt.** Die Sicherung selbst ist es (gegen ein eingehängtes
> Laufwerk auf dem Entwicklungsrechner) — das Einhängen auf dem Pi wartet auf das Gerät und
> gehört zur Abnahme von Stufe 10.

Raspberry Pi OS **Lite** hat keinen Desktop und damit keinen Automounter: Ein eingesteckter Stick
taucht von allein nirgends auf. Der Admin-Bereich sähe nie einen und meldete ewig „Bitte USB-Stick
einstecken".

```bash
sudo install -m 755 deploy/pi/photomap-usb-mount /usr/local/sbin/
sudo install -m 644 deploy/pi/99-photomap-usb.rules /etc/udev/rules.d/
sudo udevadm control --reload
```

Prüfen: Stick einstecken, dann

```bash
ls /media && findmnt /media/*
```

Zwei Fallstricke stecken darin, beide still:

**Der Container sieht den Stick nicht.** Ein Docker-Bind-Mount zeigt nur, was beim Start des
Containers schon eingehängt war. Ein später eingesteckter Stick bleibt unsichtbar — ohne
Fehlermeldung, der Ordner ist einfach leer. Dagegen steht `:rshared` an der Zeile `/media:/media`
in [`deploy/docker-compose.yml`](../deploy/docker-compose.yml). Fehlt es, hilft auch kein Neustart
des Containers zur richtigen Zeit.

**Der Stick ist da, aber schreibgeschützt.** FAT- und exFAT-Sticks kennen keine Besitzer; ohne
`uid=1000` beim Einhängen gehören sie root, und der Dienst (UID 1000, siehe
`backend/Dockerfile`) darf nicht schreiben. Das Skript setzt die Option — der Admin-Bereich
blendet solche Laufwerke aber ohnehin aus, statt einen Knopf anzubieten, der später scheitert.

**Auf dem Mac zum Entwickeln:** `PHOTOMAP_MEDIA_DIR=/Volumes` in die `.env`. Ein Prüfvolumen
entsteht mit

```bash
hdiutil create -size 200m -fs "HFS+" -volname TESTSTICK teststick.dmg && hdiutil attach teststick.dmg
```

---

## Wo die Sicherung liegt

Auf dem Stick im Ordner `photomap-sicherung/`:

```
photomap-sicherung/
  sicherung.json     Datum, Anzahl, Ortsname
  photomap.db        die Angaben, mit VACUUM INTO konsistent herausgeschrieben
  photos/            die Originale, nach ihrem Hash abgelegt
  thumbs/            die Vorschaubilder
  region.json        Kartenausschnitt
  places.json        Ortsverzeichnis
```

Ordner statt Archiv: Eine abgebrochene Sicherung ist so teilweise brauchbar statt komplett
wertlos, und die Bilder lassen sich an jedem Rechner ansehen.

Nach einer **Wiederherstellung** liegt der bisherige Stand unter `data/vorher-<Datum>/` — inklusive
Datenbank und Write-Ahead-Log. Er wird nie automatisch gelöscht. Wenn feststeht, dass alles stimmt:

```bash
rm -rf data/vorher-2026-07-29-1115
```

Das ist der einzige Ort, an dem die SD-Karte unbemerkt volllaufen kann.

Das Gerät für einen anderen Ort einrichten: [adaption.md](adaption.md).
