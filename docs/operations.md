# Betriebshandbuch

Alles, was jemand wissen muss, der das Gerät im Museum am Laufen hält. Die Bedienung für das
Museumsteam steht in der [Kuratoren-Anleitung](usermanual.md); hier steht die Technik.

> **Auf einem echten Pi noch nicht erprobt.** Die Dateien unter `deploy/pi/` sind sorgfältig
> geschrieben und syntaktisch geprüft, aber nie gelaufen — es gab beim Bauen kein Gerät. Was
> davon zuerst hakt, gehört in diese Datei, sobald der Pi dasteht.

---

## Einen neuen Pi einrichten

Raspberry Pi OS **Lite** (64 Bit), kein Desktop. Dann:

```bash
sudo git clone <repo> /opt/photomap
sudo sh /opt/photomap/deploy/pi/setup-pi.sh
```

Das Skript installiert cage, Chromium und Docker, legt den Benutzer `photomap` an, richtet den
Kiosk-Dienst und die USB-Regel ein und schaltet die Bildschirmabschaltung ab. Danach nennt es die
vier Schritte, die es nicht selbst tun kann: `.env` anlegen, PIN setzen, Kartendaten kopieren,
Container starten.

**Kartendaten kommen vom Entwicklungsrechner**, nicht vom Pi. `make tiles` und `make places`
brauchen Internet und Rechenzeit; auf den Pi gehören nur die Ergebnisse:

```bash
rsync -a frontend/public/tiles/ pi:/opt/photomap/frontend/public/tiles/
rsync -a data/places.json       pi:/opt/photomap/data/places.json
```

**Das Wappen kommt denselben Weg.** Im Repo liegt nur ein Platzhalter — ein Gemeindewappen darf
dort nicht liegen, siehe [decisions.md](decisions.md), Punkt 21. Auf dem Gerät gehört das echte
hin:

```bash
rsync -a wappen.png pi:/opt/photomap/frontend/public/logo.png
```

Danach das Frontend neu bauen (`make prod` baut die Images ohnehin neu) — die Datei wird beim Bau
in das Abbild aufgenommen, nicht zur Laufzeit gelesen. Das Holmer Wappen liegt unter
`~/Developer/Museum/Wappen/holm-wappen.png` auf dem Entwicklungsrechner; Quelle und
Rechtelage stehen in [adaption.md](adaption.md), Abschnitt „Wappen einsetzen".

---

## Was beim Einschalten passiert

Etwa 20 Sekunden, in dieser Reihenfolge:

1. **Docker startet.** Die Container laufen mit `restart: unless-stopped` von selbst hoch. Beim
   ersten Start nach einem Update laufen die Alembic-Migrationen — deshalb kann er länger dauern.
2. **`photomap-kiosk.service` wartet auf `/api/health`.** Ohne das Warten sähen die ersten
   Besucher ein paar Sekunden lang eine Fehlerseite — und die bliebe stehen, weil Chromium nicht
   von allein neu lädt. Nach fünf Minuten startet der Dienst trotzdem: eine Fehlerseite, die
   jemand sieht und meldet, ist besser als ein schwarzer Bildschirm.
3. **`cage -- chromium --kiosk`** übernimmt den Bildschirm. Frisches Browserprofil bei jedem
   Start, damit nach einem Stromausfall nichts von gestern übrig ist.
4. **Stürzt Chromium ab, startet systemd ihn neu** (`Restart=always`, 5 s Pause).

Woran man erkennt, dass etwas hakt:

```bash
systemctl status photomap-kiosk       # läuft der Kiosk?
journalctl -u photomap-kiosk -n 50    # warum nicht?
cd /opt/photomap/deploy && docker compose ps
curl -sf http://localhost/api/health && echo " API antwortet"
```

---

## Wartungsausgang

Der Kiosk kennt keine Tastenkombination zum Beenden — das ist Absicht, ein Besucher soll nicht
versehentlich herausfallen. Der Weg hinaus geht über SSH:

```bash
sudo systemctl stop photomap-kiosk     # Bildschirm wird schwarz, Dienste laufen weiter
sudo systemctl start photomap-kiosk    # zurück in die Karte
```

Für Arbeiten am Gerät selbst genügt meist der Admin-Bereich über das Wappen — Fotos pflegen,
hochladen, sichern. SSH braucht man für Updates und Fehlersuche.

---

## Update ohne Internet

Auf dem Entwicklungsrechner einen Ordner für den Stick bauen:

```bash
docker save photomap-backend:v1.2 photomap-frontend:v1.2 -o /Volumes/STICK/photomap-update/abbilder.tar
echo v1.2 > /Volumes/STICK/photomap-update/version
# nur falls sich die Region geändert hat:
cp -r frontend/public/tiles data/places.json /Volumes/STICK/photomap-update/
```

Am Pi:

```bash
sudo sh /opt/photomap/deploy/pi/update.sh /media/STICK/photomap-update
```

Das Skript liest die Abbilder ein, trägt die Version in die `.env`, tauscht Kartendaten und
Ortsindex, startet die Container neu und wartet, bis die API antwortet. **Der Bestand wird nicht
angefasst** — Fotos und Angaben bleiben, wo sie sind.

Zwei Feinheiten stecken darin: Die Kartendaten werden erst danebengelegt und dann umbenannt, damit
ein abgebrochenes Kopieren keine halbe Kartendatei hinterlässt. Und der Ortsindex wird ausdrücklich
neu eingelesen — beim Start lädt das Backend ihn nur, wenn die Tabelle leer ist.

---

## SD-Karte klonen

Die vollständige Sicherung des Geräts, inklusive Betriebssystem. Einmal nach der Einrichtung und
nach jedem größeren Update:

```bash
# Pi herunterfahren, Karte in den Entwicklungsrechner:
sudo dd if=/dev/rdiskN bs=4m | gzip > holm-pi-2026-07-29.img.gz
```

Das ersetzt die Sicherung im Admin-Bereich **nicht** — die läuft im laufenden Betrieb und sichert
den Bestand. Der Klon sichert das eingerichtete Gerät.

---

## Bildschirm bleibt schwarz

In dieser Reihenfolge:

1. `systemctl status photomap-kiosk` — läuft der Dienst?
2. `journalctl -u photomap-kiosk -n 50` — meldet cage etwas? *„unable to open primary DRM device"*
   heißt: Die Sitzung hat kein Ausgabegerät. Dann fehlt eine der vier Zeilen `PAMName`,
   `TTYPath`, `StandardInput`, `UtmpIdentifier` in der Unit, oder der Benutzer ist nicht in den
   Gruppen `video` und `render`.
3. `docker compose ps` — laufen die Container? Wenn nicht: `docker compose logs backend`.
4. Nach zehn Minuten schwarz, obwohl vorher alles lief: `consoleblank=0` fehlt in der
   `cmdline.txt` (setzt `setup-pi.sh`, wirkt erst nach einem Neustart).

---

## Fehlersuche kurz

| Beobachtung | Erster Verdacht |
|---|---|
| Karte ohne Beschriftung | `frontend/public/basemaps/` fehlt — `make tiles` lief nicht |
| Karte grau, keine Kacheln | `frontend/public/tiles/map.pmtiles` fehlt oder ist halb kopiert |
| Ortssuche findet nichts | `data/places.json` fehlt, oder `python -m app.cli places` lief nicht |
| „Hilf mit" meldet stumm Fehler | Regionsprüfung ohne `data/region.json` — `make tiles` legt sie mit ab |
| **Anzeige normal, aber nichts lässt sich speichern** | **Schema veraltet — meist nach einer zurückgespielten Sicherung. Neu starten, [siehe unten](#eine-zurückgespielte-sicherung-passt-nicht-zum-programm)** |
| USB-Stick erscheint nicht | udev-Regel oder `:rshared` — siehe unten |
| Anmeldung lehnt jede PIN ab | `PHOTOMAP_ADMIN_PIN_HASH` leer; der Bereich sagt das im Klartext |
| Importierte Fotos ohne Schlagwort oder Bildnachweis | Eine Einstellung erreicht den Container nicht — [siehe unten](#einstellungen-im-containerbetrieb) |

---

## Die PIN für den Admin-Bereich einrichten

```bash
cd backend && .venv/bin/python -m app.cli pin
```

Der Befehl fragt die PIN zweimal ab und gibt die Zeile aus, die in die `.env` gehört. Die PIN
selbst wird nirgends gespeichert; vergessen heißt neu setzen. Danach den Dienst neu starten.

Ist keine PIN eingerichtet, sagt das Zahlenfeld genau das — es lehnt nicht stumm jede Eingabe ab.
Nach fünf Fehlversuchen sperrt es für eine Minute. Die Sitzung endet nach 30 Minuten ohne
Bedienung; jede Aktion schiebt sie hinaus, und ein Neustart des Dienstes beendet jede Sitzung.

---

## Einstellungen im Containerbetrieb

Die `.env` im Projektverzeichnis ist auch im Betrieb die Stelle, an der Einstellungen stehen. Sie
liegt bewusst **nicht** im Abbild — das Abbild ist die Software, die `.env` ist der Ort — und wird
in [`deploy/docker-compose.yml`](../deploy/docker-compose.yml) als `env_file` eingelesen. Wer dort
etwas ändert, startet danach die Container neu:

```bash
cd /opt/photomap && docker compose up -d
```

**Vier Werte setzt die Compose-Datei selbst**, und die gewinnen über die `.env`:
`PHOTOMAP_DATA_DIR`, `PHOTOMAP_MEDIA_DIR`, `PHOTOMAP_CORS_ORIGINS` und der Ort des PIN-Hashes. Sie
beschreiben den Container, nicht den Ort — innen heißen die Verzeichnisse immer `/data` und
`/media`, gleichgültig wo sie aussen liegen. Ein `PHOTOMAP_MEDIA_DIR=/Volumes` in der `.env` des
Entwicklungsmacs stört den Betrieb deshalb nicht.

**Warum das hier steht:** Bis zum 14. August 2026 reichte die Compose-Datei nur einzelne Werte
durch. Die übrigen fielen im Container still auf ihre Vorgaben zurück, und das traf ausgerechnet
den Import: Fotos kamen an, aber ohne Schlagwort, ohne Bildnachweis und ohne Herkunftsangabe.
Nichts schlug fehl, nichts stand im Protokoll. Wer heute eine neue Einstellung einführt, muss
nichts weiter tun — sie kommt von selbst durch.

---

## USB-Sticks sichtbar machen

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

## Eine zurückgespielte Sicherung passt nicht zum Programm

**Der Fall:** Eine Sicherung wurde eingespielt, die **älter ist als die letzte Programmaktualisierung**.
Die Ausstellung sieht danach völlig normal aus — Fotos, Karte, Zeitleiste —, aber **jeder Schreibzugriff
scheitert**: Besucherbeiträge, Bearbeitungen in der Verwaltung, Uploads. Der Besucher liest eine
Fehlermeldung statt eines Dankeschöns.

**Der Grund.** Die Sicherung enthält `photomap.db` genau so, wie die Datei damals aussah — mitsamt
ihrem Schemastand in der Tabelle `alembic_version`. Beim Zurückspielen wird die Datei **im Ganzen**
ausgetauscht (`_swap_in` in `services/backup.py`); danach hängt sich das laufende Programm nur neu
an sie (`_reopen_database`). **Migrationen laufen dabei nicht.** Sie laufen beim *Start*
(`backend/docker-entrypoint.sh`: `alembic upgrade head`), und eine Wiederherstellung ist kein Start.

Fehlt dem Schema also eine Spalte, die das heutige Programm schreiben will, endet jeder Schreibversuch
mit einem HTTP 500 und im Protokoll steht:

```
sqlite3.OperationalError: table changes has no column named old_source
```

### Die Abhilfe: neu starten

```bash
cd /opt/photomap && docker compose restart backend
```

Oder schlicht das Gerät aus- und einschalten. Der Start bringt das Schema auf Stand; der Bestand
bleibt unberührt. **Das ist der Normalfall und reicht fast immer** — deshalb steht im
[Benutzerhandbuch](usermanual.md#danach-einmal-neu-starten) nur dieser eine Satz.

### Nachsehen, ob es daran lag

```bash
docker compose exec backend python -c "import sqlite3; print(sqlite3.connect('/data/photomap.db').execute('select * from alembic_version').fetchone())"
docker compose exec backend alembic heads
```

Stimmen die beiden Werte nicht überein, war es das. Auf dem Entwicklungsrechner dasselbe ohne
Container:

```bash
sqlite3 data/photomap.db "select * from alembic_version;"
cd backend && .venv/bin/alembic heads
```

Und die Reparatur von Hand, falls der Neustart nicht greift:

```bash
make migrate
```

### Wenn die Sicherung **neuer** ist als das Programm

Der umgekehrte Fall, und er ist der unangenehmere: Eine Sicherung von einem aktuelleren Gerät auf
ein älteres zurückzuspielen bringt ein Schema mit, das dieses Programm nicht kennt. `alembic` weiß
dann mit der eingetragenen Revision nichts anzufangen und **bricht beim Start ab** — das Gerät kommt
nicht hoch.

**Abhilfe: erst das Programm aktualisieren, dann die Sicherung einspielen.** Siehe
[Update ohne Internet](#update-ohne-internet). Der bisherige Stand liegt derweil unter
`data/vorher-<Datum>/` und lässt sich zurückholen, indem man `photomap.db`, `photos/` und `thumbs/`
von dort wieder nach `data/` schiebt.

**Die Regel dahinter, für beide Richtungen:** *Erst das Programm auf den Stand bringen, den die
Sicherung braucht — dann einspielen — dann neu starten.*

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
