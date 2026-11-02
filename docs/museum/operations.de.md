<!-- translated-from: docs/museum/operations.md -->
<!-- source-sha: 942bb3f7a37e578a460c3e4a05f7cb23568214aeb5ae72015d4699368c0fa914 -->

# Betriebshandbuch

Alles, was jemand wissen muss, der das Gerät im Museum am Laufen hält. Die Bedienung steht in der
[Anleitung für das Museumsteam](usermanual.de.md); hier steht die Technik.

> **Erprobt auf einem Raspberry Pi 4 mit Raspberry Pi OS auf Debian 13, am 1. und 2. November
> 2026:** das Einrichten aus dem Paket, der Kiosk nach einem Neustart, Touch, das Zurückspielen
> einer Sicherung vom USB-Stick und das Aktualisieren mit der Sammlung auf dem Gerät. **Noch nicht
> erprobt:** ein Stromausfall und eine Sicherung vom Gerät auf einen Stick.

---

## Was der Entwicklungsrechner braucht

Einmal, vor dem ersten Pi. Alles, was das Gerät bekommt, wird auf dem Entwicklungsrechner
zusammengestellt; nach dem Einrichten braucht der Pi weder git noch das Internet.

**Die Karte und den Ortsindex**, aus `make tiles` und `make places`. Beide brauchen das Internet
und Rechenzeit, deshalb laufen sie hier und nicht auf dem Pi.

**Den Ordner `local/`.** Er enthält, was zu diesem Museum gehört und nicht ins Repository darf.
Git übergeht ihn.

| Datei | Inhalt |
|---|---|
| `local/logo.png` | das Wappen des Ortes |
| `local/pi.env` | die `.env` des Pi |

Das Wappen:

```bash
mkdir -p local
cp ~/Developer/Museum/Wappen/holm-wappen.png local/logo.png
```

Es kommt beim Bauen in das Frontend-Abbild. `frontend/public/logo.png` bleibt der Platzhalter, dort
ist nichts zu ändern. Quelle und Rechtelage stehen in [adaption.de.md](adaption.de.md), Abschnitt
„Wappen einsetzen". Ein Museum ohne Wappen kopiert den Platzhalter nach `local/logo.png`.

**`local/pi.env`** legt das erste `make deploy` aus der Vorlage an und hält dann an. Zwei Dinge
gehören hinein:

- **Die PIN-Zeile.** `make pin` fragt die PIN zweimal ab und gibt die Zeile
  `KIEKMAP_ADMIN_PIN_HASH='…'` aus. **Die einfachen Anführungszeichen bleiben stehen.** Der Hash
  enthält `$`-Zeichen, und ohne Anführungszeichen schneidet Compose ihn am ersten ab: die PIN passt
  dann nie.
- **Die Einstellungen der Sammlung**, aus
  [Schritt 5 der Anpassung](adaption.de.md#5-sammlungsspezifisches-prüfen).

`KIEKMAP_VERSION` bleibt, wie es ist; das schreiben die Skripte auf dem Pi.

**Einen Namen für den Pi in SSH.** In `~/.ssh/config`:

```
Host kiekmap-pi
    HostName kiekmap.local
    User admin
```

`kiekmap.local` ist der im Imager gesetzte Rechnername, `admin` der dort angelegte Benutzer. Dann
einmal der Schlüssel:

```bash
ssh-copy-id kiekmap-pi
```

Danach muss `ssh kiekmap-pi` eine Shell öffnen, ohne nach einem Kennwort zu fragen. `make deploy`
nimmt den Namen `kiekmap-pi`; ein anderer wird als `host=` übergeben.

---

## Einen neuen Pi einrichten

Ein **Raspberry Pi 4 oder 5**. Die Karte braucht WebGL 2, und ein Pi 3 bietet es nicht: die Karte
bliebe dort grau.

**1. Das Betriebssystem.** Mit dem Raspberry Pi Imager: Raspberry Pi OS **Lite** (64 Bit), ohne
Desktop. In den Einstellungen des Imagers: der Rechnername `kiekmap`, ein Benutzer mit Kennwort,
SSH eingeschaltet, und das WLAN, falls kein Kabel steckt. Der Pi braucht beim Einrichten das
Internet, denn er installiert Chromium und Docker. **Ein Netzwerkkabel ist besser als WLAN:**
Chromium allein hat 120 MB, und beim ersten Pi brauchte das WLAN dafür eine Viertelstunde.

**2. Das Paket, auf dem Entwicklungsrechner:**

```bash
make deploy
```

`make deploy` baut beide Abbilder mit dem Wappen. Es legt sie mit der Karte, dem Ortsindex, den
Skripten und `local/pi.env` in `release/kiekmap/` zusammen und kopiert den Ordner nach `~/kiekmap`
auf dem Pi. Es verweigert einen Arbeitsbaum, der nicht sauber ist, und nennt, was fehlt: Karte,
Ortsindex, Wappen oder PIN.

Das Paket trägt die Version des Commits, aus dem es gebaut ist: `v0.9.6` auf dem Fassungs-Tag,
`v0.9.6-g0942491` auf jedem anderen Commit.

**3. Auf dem Pi**, nach `ssh kiekmap-pi`:

```bash
sudo sh ~/kiekmap/deploy/pi/setup-pi.sh
```

`sudo` fragt nach dem Kennwort des im Imager angelegten Benutzers. Direkt vom Entwicklungsrechner
aus gestartet, braucht diese Abfrage das `-t`: `ssh -t kiekmap-pi 'sudo sh ~/kiekmap/deploy/pi/setup-pi.sh'`.

Das Skript installiert cage, Chromium und Docker und legt den Benutzer `kiekmap` an, der den Kiosk
betreibt. Es kopiert die Software nach `/opt/kiekmap`, richtet den Kiosk-Dienst, die USB-Regel und
den Ausschaltknopf ein und schaltet die Bildschirmabschaltung ab. Dann lädt es die Abbilder,
startet sie und wartet, bis die API antwortet. **Ein Gerät, das schon eine Sammlung hat, verweigert
es**; dafür gibt es das Aktualisieren.

**4. Neu starten:** `sudo reboot`. Der Pi landet ohne Tastatur in der Karte.

**5. Die Sammlung.** Sie ist nach dem Einrichten leer. Den Stick mit der Sicherung einstecken, über
das Wappen den Admin-Bereich öffnen und die Sicherung dort zurückspielen.

`~/kiekmap` wird danach nicht mehr gebraucht: `rm -r ~/kiekmap`.

**Was auf dem Pi wo liegt:**

| Pfad | Inhalt | Gehört |
|---|---|---|
| `/opt/kiekmap/data/` | die Sammlung: Datenbank, Fotos, Ortsindex | UID 1000, dem Backend im Container |
| `/opt/kiekmap/.env` | die Einstellungen, samt PIN-Hash | root, lesbar für die Gruppe `docker` |
| `/opt/kiekmap/deploy/` | Compose-Datei und Skripte | root |
| `/opt/kiekmap/frontend/public/tiles/` | die Karte | root |
| `/opt/kiekmap/pre-update/` | die Datenbank vor den letzten beiden Updates | root |

Jeder `docker compose`-Befehl auf dem Pi läuft deshalb mit `sudo`.

---

## Was beim Einschalten passiert

Etwa 20 Sekunden, in dieser Reihenfolge:

1. **Docker startet.** Die Container laufen mit `restart: unless-stopped` von selbst hoch. Beim
   ersten Start nach einem Update laufen die Alembic-Migrationen — deshalb kann er länger dauern.
2. **`kiekmap-kiosk.service` wartet auf `/api/health`.** Ohne das Warten sähen die ersten
   Besucher ein paar Sekunden lang eine Fehlerseite — und die bliebe stehen, weil Chromium nicht
   von allein neu lädt. Nach fünf Minuten startet der Dienst trotzdem: eine Fehlerseite, die
   jemand sieht und meldet, ist besser als ein schwarzer Bildschirm.
3. **`cage -- chromium --kiosk`** übernimmt den Bildschirm. Frisches Browserprofil bei jedem
   Start, damit nach einem Stromausfall nichts von gestern übrig ist.
4. **Stürzt Chromium ab, startet systemd ihn neu** (`Restart=always`, 5 s Pause).

Woran man erkennt, dass etwas hakt:

```bash
systemctl status kiekmap-kiosk       # läuft der Kiosk?
journalctl -u kiekmap-kiosk -n 50    # warum nicht?
cd /opt/kiekmap && sudo docker compose -f deploy/docker-compose.yml --env-file .env ps
curl -sf http://localhost/api/health && echo " API antwortet"
```

---

## Ausschalten aus der Verwaltung

Der Knopf unten auf der Startseite der Verwaltung, und die drei Teile dahinter:

1. Das Backend schreibt `data/shutdown-requested`, mit der Uhrzeit darin. Es läuft ohne Rechte in
   einem Container und kann nicht mehr als das.
2. `kiekmap-shutdown.path` sieht die Datei und startet `kiekmap-shutdown.service`.
3. `/usr/local/sbin/kiekmap-shutdown` löscht die Anforderung, prüft, ob sie aus diesem Start
   stammt, und ruft `systemctl --no-block poweroff` auf.

```bash
systemctl status kiekmap-shutdown.path      # läuft die Überwachung?
journalctl -u kiekmap-shutdown -n 20        # was bei der letzten Anforderung geschah
```

**`data/shutdown-watcher` ist es, was den Knopf wirken lässt.** `setup-pi.sh` schreibt die Datei, und
`update.sh` schreibt sie erneut. Ohne sie verweigert das Backend, denn dasselbe Programm läuft auch
auf einem Entwicklungsrechner und online, wo niemand die Anforderung ausführen würde.

**Die Container werden absichtlich nicht gestoppt.** `docker compose stop` markiert sie als von Hand
gestoppt, und `restart: unless-stopped` ließe sie beim nächsten Start unten. systemd hält Docker
selbst an, und die Datenbank übersteht das: WAL mit `synchronous=NORMAL` kostet höchstens die letzte
Transaktion.

**Den Stecker zu ziehen bleibt überstehbar**, und darum geht es in [Issue #21](https://github.com/nordfisch/kiekmap/issues/21):
Der Knopf ist der geordnete Weg, keine Reparatur. Nicht abgedeckt ist der Fall, dass ihn niemand
drückt.

---

## Wartungsausgang

Der Kiosk kennt keine Tastenkombination zum Beenden — das ist Absicht, damit ein Besucher die
Ausstellung nicht versehentlich verlässt. Der Weg hinaus geht über SSH:

```bash
sudo systemctl stop kiekmap-kiosk     # Bildschirm wird schwarz, Dienste laufen weiter
sudo systemctl start kiekmap-kiosk    # zurück in die Karte
```

Für Arbeiten am Gerät selbst genügt meist der Admin-Bereich über das Wappen — Fotos pflegen,
hochladen, sichern. SSH braucht man für Updates und Fehlersuche.

---

## Aktualisieren

**1. Eine Sicherung**, im Admin-Bereich, auf einen Stick. Das Update behält die Sammlung, aber eine
Sicherung ist die eine Kopie, die nicht auf dem Gerät liegt.

**2. Das Paket, auf dem Entwicklungsrechner**, aus der Fassung, die installiert wird:

```bash
git switch --detach v0.9.6
make deploy
```

**3. Auf dem Pi**, nach `ssh kiekmap-pi`:

```bash
sudo sh ~/kiekmap/deploy/pi/update.sh
```

Das Skript, in dieser Reihenfolge:

1. lädt die neuen Abbilder, während die alte Version weiterläuft;
2. hält die Container an und kopiert die Datenbank nach `pre-update/<alte Version>/`. Die letzten
   beiden Kopien bleiben;
3. ersetzt `deploy/` und die Karte. Beide werden erst neben die alten kopiert und dann umbenannt,
   damit eine halb abgebrochene Kopie keine halbe Kartendatei hinterlässt;
4. schreibt die neue Version in `KIEKMAP_VERSION`;
5. übernimmt den Ortsindex nur, wenn er sich von dem auf dem Gerät unterscheidet, und liest ihn
   dann ein;
6. startet die Container, wartet auf die API und prüft, dass das Backend das neue Abbild fährt;
7. startet den Kiosk neu und entfernt die Abbilder, die älter sind als die vorige Version.

**Was bleibt:** alles in `data/` — Fotos, Datenbank, der Stand der Sicherung — und die `.env`, bis
auf `KIEKMAP_VERSION`. Eine Änderung an `local/pi.env` erreicht ein schon eingerichtetes Gerät
deshalb nicht. Eine geänderte Einstellung wird auch auf dem Pi eingetragen:

```bash
sudo nano /opt/kiekmap/.env
cd /opt/kiekmap && sudo docker compose -f deploy/docker-compose.yml --env-file .env up -d
```

**Ein Gerät, das nicht eingerichtet ist, verweigert das Skript**; dafür gibt es `setup-pi.sh`.

**Eine abreißende Verbindung hält es nicht auf.** Beide Skripte starten sich selbst noch einmal als
systemd-Unit, `kiekmap-update` und `kiekmap-setup-pi`, und das Terminal zeigt nur deren Ausgabe.
Nach einem neuen `ssh kiekmap-pi` zeigt `journalctl -u kiekmap-update`, wie weit es gekommen ist.

**Zurück.** Das Skript gibt die Befehle dafür am Ende aus. Das Abbild der vorigen Version bleibt
auf dem Gerät, und die Datenbank von vor dem Update liegt in `pre-update/`. Was nach dem Update
eingegeben wurde, geht auf diesem Weg verloren.

### Aktualisieren per Stick

Der Pi im Museum hängt an keinem Netz. Dasselbe Paket kommt dann auf einen Stick, auf dem
Entwicklungsrechner:

```bash
make deploy to=/Volumes/STICK/kiekmap
```

`to=` nennt einen eigenen Ordner auf dem Stick, nicht den Stick selbst: ein früheres Paket darin
wird ersetzt, alles andere verweigert. Auf dem Pi, mit eingestecktem Stick:

```bash
ls /media
sudo sh /media/<Name des Sticks>/kiekmap/deploy/pi/update.sh
```

Das Skript findet das Paket neben sich und tut dasselbe wie oben.

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

1. `systemctl status kiekmap-kiosk` — läuft der Dienst?
2. `journalctl -u kiekmap-kiosk -n 50` — meldet cage etwas? *„unable to open primary DRM device"*
   heißt: Die Sitzung hat kein Ausgabegerät. Dann fehlt eine der vier Zeilen `PAMName`,
   `TTYPath`, `StandardInput`, `UtmpIdentifier` in der Unit, oder der Benutzer ist nicht in den
   Gruppen `video` und `render`.
3. `docker compose ... ps` — laufen die Container? Wenn nicht: `... logs backend`. Der vollständige
   Befehl steht unter [Einstellungen im Containerbetrieb](#einstellungen-im-containerbetrieb).
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
| **Anzeige normal, aber nichts lässt sich speichern** | **Schema veraltet. Seit August 2026 zieht die Wiederherstellung es selbst nach — [siehe unten](#der-schemastand-einer-zurückgespielten-sicherung)** |
| USB-Stick erscheint nicht | udev-Regel oder `:rshared` — siehe unten |
| Der Knopf meldet, das Gerät könne sich nicht abschalten | `data/shutdown-watcher` fehlt — `update.sh` noch einmal laufen lassen |
| Anmeldung lehnt jede PIN ab | `KIEKMAP_ADMIN_PIN_HASH` leer; der Bereich sagt das im Klartext |
| Importierte Fotos ohne Schlagwort oder Bildnachweis | Eine Einstellung erreicht den Container nicht — [siehe unten](#einstellungen-im-containerbetrieb) |

---

## Die PIN für den Admin-Bereich einrichten

```bash
cd backend && .venv/bin/python -m app.cli pin
```

`make pin` tut dasselbe. Das ist der Entwicklungsrechner. **Auf dem Gerät gibt es keine virtuelle
Umgebung** — der Pi trägt die Software als Abbild, nicht als Python-Installation, deshalb läuft
derselbe Befehl dort im Container:

```bash
cd /opt/kiekmap && sudo docker compose -f deploy/docker-compose.yml --env-file .env \
    run --rm backend python -m app.cli pin
```

Der Befehl fragt die PIN zweimal ab und gibt die Zeile aus, die in die `.env` gehört, in einfachen
Anführungszeichen. Die Anführungszeichen bleiben: ohne sie schneidet Compose den Hash am ersten `$`
ab. Die PIN selbst wird nirgends gespeichert; vergessen heißt neu setzen.

Auf einem Gerät kommt die Zeile in `/opt/kiekmap/.env` (`sudo nano`), gefolgt vom `up -d` aus
[Aktualisieren](#aktualisieren). Sie kommt auch in `local/pi.env`, damit das nächste eingerichtete
Gerät sie bekommt.

Ist keine PIN eingerichtet, sagt das Zahlenfeld genau das — es lehnt nicht stumm jede Eingabe ab.
Nach fünf Fehlversuchen sperrt es für eine Minute. Die Sitzung endet nach 30 Minuten ohne
Bedienung; jede Aktion schiebt sie hinaus, und ein Neustart des Dienstes beendet jede Sitzung.

---

## Einstellungen im Containerbetrieb

Die `.env` im Projektverzeichnis ist auch im Betrieb die Stelle, an der Einstellungen stehen. Sie
liegt bewusst **nicht** im Abbild — das Abbild ist die Software, die `.env` ist der Ort — und wird
in [`deploy/docker-compose.yml`](../../deploy/docker-compose.yml) als `env_file` eingelesen. Wer dort
etwas ändert, startet danach die Container neu:

```bash
cd /opt/kiekmap && docker compose -f deploy/docker-compose.yml --env-file .env up -d
```

**Aus `/opt/kiekmap` und mit `--env-file`, nicht aus `deploy/`.** Compose liest die `.env` aus dem
Verzeichnis, in dem es gestartet wird, und die `.env` liegt eine Ebene über der Compose-Datei. Aus
`deploy/` heraus fände es sie nicht: `KIEKMAP_VERSION` fiele auf `dev` zurück, und weil die
Compose-Datei ein `build:` trägt, würde der Pi bei fehlendem Abbild das Frontend selbst bauen. Jeder
`docker compose`-Befehl auf dem Gerät hat diese Form.

**Die Sprache des Geräts** steht ebenfalls hier:

```bash
KIEKMAP_LANGUAGE=de     # oder en
```

Sie schaltet Besucheransicht, Verwaltung, Meldungen und Datumsbeschriftung um. **Ein neuer Bau ist
nicht nötig** — nach dem Neustart der Container gilt der neue Wert. Ein anderer Wert als `de` oder
`en` bricht den Start ab, statt still auf Deutsch zurückzufallen; im Protokoll steht dann eine
Zeile von Pydantic. Mehr in [adaption.de.md](adaption.de.md#andere-sprache).

**Drei Werte setzt die Compose-Datei selbst**, und die gewinnen über die `.env`:
`KIEKMAP_DATA_DIR`, `KIEKMAP_MEDIA_DIR` und der Ort des PIN-Hashes. Sie
beschreiben den Container, nicht den Ort — innen heißen die Verzeichnisse immer `/data` und
`/media`, gleichgültig wo sie außen liegen. Ein `KIEKMAP_MEDIA_DIR=/Volumes` in der `.env` des
Entwicklungsmacs stört den Betrieb deshalb nicht.

**Warum das hier steht:** Bis zum 14. August 2026 reichte die Compose-Datei nur einzelne Werte
durch. Die übrigen fielen im Container still auf ihre Vorgaben zurück, und das traf ausgerechnet
den Import: Fotos kamen an, aber ohne Schlagwort, ohne Bildnachweis und ohne Herkunftsangabe.
Nichts schlug fehl, nichts stand im Protokoll. Wer heute eine neue Einstellung einführt, muss
nichts weiter tun — sie kommt von selbst durch; geprüft ist das sowohl über den Eingangsordner als
auch über den Stapel-Upload der Verwaltung.

---

## USB-Sticks sichtbar machen

Raspberry Pi OS **Lite** hat keinen Desktop und damit keinen Automounter: Ein eingesteckter Stick
taucht von allein nirgends auf. Der Admin-Bereich sähe nie einen und meldete ewig „Bitte USB-Stick
einstecken".

```bash
sudo install -m 755 deploy/pi/kiekmap-usb-mount /usr/local/sbin/
sudo install -m 644 deploy/pi/99-kiekmap-usb.rules /etc/udev/rules.d/
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
in [`deploy/docker-compose.yml`](../../deploy/docker-compose.yml). Fehlt es, hilft auch kein Neustart
des Containers zur richtigen Zeit.

**Der Stick ist da, aber schreibgeschützt.** FAT- und exFAT-Sticks kennen keine Besitzer; ohne
`uid=1000` beim Einhängen gehören sie root, und der Dienst (UID 1000, siehe
`backend/Dockerfile`) darf nicht schreiben. Das Skript setzt die Option — der Admin-Bereich
blendet solche Laufwerke aber ohnehin aus, statt einen Knopf anzubieten, der später scheitert.

**Auf dem Mac zum Entwickeln:** `KIEKMAP_MEDIA_DIR=/Volumes` in die `.env`. Ein Prüfvolumen
entsteht mit

```bash
hdiutil create -size 200m -fs "HFS+" -volname TESTSTICK teststick.dmg && hdiutil attach teststick.dmg
```

> **In `/Volumes` liegt immer ein Symlink auf `/`**, benannt nach dem internen Volume — das legt
> macOS selbst an. Bis zum 14. August 2026 galt er als Datenträger, und die Sicherung landete
> dahinter, im laufenden Datenverzeichnis. Seither werden Symlinks übersprungen
> ([decisions.md](../developer/decisions.md), Punkt 40); die Liste ist auf einem Mac ohne angestecktes
> Laufwerk jetzt leer, und genau das ist richtig.

---

## Der Schemastand einer zurückgespielten Sicherung

**Seit dem 15. August 2026 regelt das die Wiederherstellung selbst** — dieser Abschnitt beschreibt,
*wie*, und was zu tun ist, wenn doch etwas hakt. Der kurze Weg für das Team steht in der
[Anleitung](usermanual.de.md#wenn-die-sicherung-älter-ist-als-das-programm).

**Warum es überhaupt eine Frage ist.** Eine Sicherung enthält `kiekmap.db` genau so, wie die Datei
damals aussah — mitsamt ihrem Schemastand in der Tabelle `alembic_version`. Beim Zurückspielen wird
die Datei **im Ganzen** ausgetauscht (`_swap_in` in `services/backup/restore.py`). Für diese
Sekunden schließt das Programm die Datenbank und hängt sich danach an die neue Datei
(`closed_for_swap` in `app/db.py`). Migrationen laufen dabei nicht von
selbst: Sie laufen beim *Start* (`backend/docker-entrypoint.sh`), und eine Wiederherstellung ist
kein Start.

**Was jetzt passiert**, und die Reihenfolge ist der ganze Punkt (`services/schema.py`):

| Die Sicherung ist … | … und dann |
|---|---|
| **älter** als das Programm | wird nach dem Tausch `alembic upgrade head` gefahren. Auf dem Balken steht „Der Schemastand wird nachgezogen" |
| **auf dem gleichen Stand** | passiert nichts, der Aufruf ist folgenlos |
| **neuer** als das Programm | **bricht ab, bevor irgendetwas getauscht ist** — der Bestand auf dem Gerät bleibt unangetastet |

Die Ablehnung kommt **vor** dem Tausch, und das ist keine Feinheit: Eine Sicherung, die dieses
Programm nicht lesen kann, darf das Gerät nicht halb ersetzt zurücklassen. Nach der Ablehnung liegt
das Archiv weiterhin im Eingangsordner, der Arbeitsordner ist aufgeräumt.

**Bei einer zu neuen Sicherung: erst das Programm aktualisieren, dann einspielen.** Siehe
[Aktualisieren](#aktualisieren).

### Nachsehen, wo etwas steht

```bash
docker compose -f deploy/docker-compose.yml --env-file .env exec backend python -c "import sqlite3; print(sqlite3.connect('/data/kiekmap.db').execute('select * from alembic_version').fetchone())"
docker compose -f deploy/docker-compose.yml --env-file .env exec backend alembic heads
```

Stimmen die beiden Werte nicht überein, ist das Schema nicht auf Stand. Das ist bei
Schreibfehlern im Betrieb der erste Blick, und der Zustand ist von außen nicht zu sehen: Die
Ausstellung zeigt Fotos, Karte und Zeitleiste wie immer, nur **jeder Schreibzugriff** scheitert
mit HTTP 500. Auf dem Entwicklungsrechner dasselbe ohne Container:

```bash
sqlite3 data/kiekmap.db "select * from alembic_version;"
cd backend && .venv/bin/alembic heads
```

Und die Reparatur von Hand:

```bash
make migrate
```

## Die Online-Instanz

Neben dem Pi gibt es einen zweiten Weg, dies zu betreiben: auf einem Webserver, von überall
erreichbar, hinter einem Kennwort. Er ist für die Monate da, in denen das Museumsteam die Datenbank
von zu Hause aus füllt, bevor ein Gerät im Ausstellungsraum steht.

Dort laufen dieselben zwei Container wie auf dem Pi — dieselben Abbilder, dieselbe
nginx-Konfiguration. Nur Caddy steht davor und kümmert sich um HTTPS und das Kennwort:

```
Internet --HTTPS--> Caddy --HTTP--> nginx (frontend) --> uvicorn (backend)
```

**Das Kennwort schützt alles**, die Karte eingeschlossen und `/api/` ebenso. Wer es nicht hat,
bekommt eine 401 und sieht nichts. Genau dafür ist diese Instanz da: Die Sammlung ist nicht
öffentlich, solange sie aufgebaut wird.

**Die Sicherung ist der ZIP-Download.** Ein Server hat keine USB-Anschlüsse, der Sicherungsknopf im
Admin-Bereich findet dort also kein Ziel. Stattdessen lädt jemand das Archiv im Admin-Bereich
herunter, regelmäßig, und bewahrt es anderswo auf. Der Stick ist für das Gerät im Museum.

**Die PIN bekommt mehr Ziffern.** Auf dem Pi reichen vier — wer davorsteht, steht im Museum. Online
reichen vier nicht; die PIN erlaubt bis zu zwölf.

**Zwei Befehle laufen nie auf dem Server.** `deploy/pi/update.sh` startet die Container ohne Caddy:
nginx antwortet dann auf Port 80, und niemand wird nach einem Kennwort gefragt. `make prod-web`
baut die Abbilder auf dem Server selbst und bleibt im Vordergrund. Die Abbilder kommen vom
Entwicklungsrechner, wie beim Pi.

### Was der Server braucht

- **Einen Linux-Rechner mit öffentlicher Adresse und SSH-Zugang.** Die Befehle unten sind für
  Oracle Linux 9 auf einer Ampere-Instanz von Oracle Cloud geschrieben. Eine andere Distribution
  unterscheidet sich darin, wie Docker installiert und die Firewall geöffnet wird.
- **Einen Domainnamen, dessen A-Eintrag auf diese Adresse zeigt.** Caddy fragt bei Let's Encrypt
  ein Zertifikat für diesen Namen an.
- **Den Prozessor des Entwicklungsrechners, oder einen Schalter.** Die Abbilder werden dort gebaut
  und laufen nur auf derselben Architektur. Ein Mac mit Apple-Chip und eine Ampere-Instanz sind
  beide `arm64` und passen zusammen. Für einen `x86_64`-Server gehört
  `DOCKER_DEFAULT_PLATFORM=linux/amd64` vor `make release`. `uname -m` auf dem Server sagt, welcher
  es ist.

**Ein Name für den Server, auf dem Entwicklungsrechner.** Jeder Befehl unten erreicht den Server
über einen SSH-Alias, damit seine Adresse an einer Stelle steht. In `~/.ssh/config`:

```
Host kiekmap-web
    HostName <Adresse des Servers>
    User opc
```

`opc` ist der Benutzer, den Oracle anlegt. Andere Anbieter nennen ihn anders. Danach muss
`ssh kiekmap-web` eine Shell auf dem Server öffnen.

### Den Server einrichten

Einmal. Die ersten vier Schritte auf dem Server, nach `ssh kiekmap-web`.

**1. Die Ports öffnen.** 80 für das Zertifikat, 443 für die Seite. In der Konsole des Anbieters —
bei Oracle Cloud eine Eingangsregel für TCP 80 und 443 in der Security List des Subnetzes der
Instanz — und in der Firewall des Rechners:

```bash
sudo firewall-cmd --permanent --add-service=http --add-service=https && sudo firewall-cmd --reload
```

**2. Docker und git:**

```bash
sudo dnf -y install dnf-plugins-core git
sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo dnf -y install docker-ce docker-ce-cli containerd.io docker-compose-plugin
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
```

Ab- und wieder anmelden, damit die Gruppe gilt. `docker run --rm hello-world` muss danach ohne
`sudo` funktionieren.

**3. Das Repository und die `.env`:**

```bash
sudo mkdir -p /opt/kiekmap && sudo chown $USER:$USER /opt/kiekmap
git clone https://github.com/nordfisch/kiekmap.git /opt/kiekmap
mkdir -p /opt/kiekmap/data
cp /opt/kiekmap/deploy/.env.example /opt/kiekmap/.env
```

**4. Was in die `.env` gehört.** Die drei Zeilen der Online-Instanz, die PIN und die Einstellungen
der Sammlung aus [Schritt 5 der Übernahme](adaption.de.md#5-sammlungsspezifisches-prüfen):

```bash
KIEKMAP_WEB_DOMAIN=fotos.example.org
KIEKMAP_WEB_USER=museum
KIEKMAP_WEB_PASSWORD_HASH=$$2a$$14$$...
KIEKMAP_ADMIN_PIN_HASH=...
```

Der Kennwort-Hash, auf dem Entwicklungsrechner:

```bash
docker run --rm caddy:2.11.4-alpine caddy hash-password --plaintext '<Kennwort>'
```

**Jedes `$` darin muss in der `.env` doppelt geschrieben werden.** Compose liest ein einzelnes als
Anfang eines Variablennamens und verwirft, was darauf folgt — das Kennwort passt dann nie, und
nichts sagt, warum. Der PIN-Hash kommt von `make pin` auf dem Entwicklungsrechner, in einfachen
Anführungszeichen, die ihn auf dieselbe Weise schützen; siehe
[Die PIN einrichten](#die-pin-für-den-admin-bereich-einrichten).

**5. Die Kartendaten**, auf dem Entwicklungsrechner, aus `make tiles` und `make places`:

```bash
rsync -a frontend/public/tiles/ kiekmap-web:/opt/kiekmap/frontend/public/tiles/
rsync -a data/places.json       kiekmap-web:/opt/kiekmap/data/places.json
```

**6. Die Software:** die Schritte von [Den Server aktualisieren](#den-server-aktualisieren). Auf
einem frischen Server sind sie der erste Start. Die Sammlung ist danach leer; sie wird im
Admin-Bereich gefüllt, oder indem dort eine Sicherung eingelesen wird.

### Den Server aktualisieren

Bei jeder Fassung. Die Version in den Befehlen ist ein Beispiel; es gilt die, die installiert wird.

**1. Eine Sicherung.** Das ZIP im Admin-Bereich der Online-Instanz herunterladen.

**2. Die Abbilder, auf dem Entwicklungsrechner**, gebaut aus der Fassung:

```bash
git switch --detach v0.9.6
make release to=$HOME/kiekmap-update
```

`make release` schreibt `images.tar` und eine `version`-Datei. Das Wappen kommt aus
`local/logo.png`, wie für den Pi; siehe
[Was der Entwicklungsrechner braucht](#was-der-entwicklungsrechner-braucht). Ohne diese Datei trägt
das Abbild den Platzhalter.

**3. Auf den Server**, in das Heimatverzeichnis des Server-Benutzers — `/opt` gehört root, und
übergeben wurde nur `/opt/kiekmap`:

```bash
rsync -a --progress $HOME/kiekmap-update/ kiekmap-web:kiekmap-update/
```

**4. Auf dem Server**, nach `ssh kiekmap-web`:

```bash
cd /opt/kiekmap
git fetch --tags && git switch --detach v0.9.6
docker load -i ~/kiekmap-update/images.tar
sed -i 's/^KIEKMAP_VERSION=.*/KIEKMAP_VERSION=v0.9.6/' .env
docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.web.yml --env-file .env up -d
```

- Der Klon folgt der Fassung, weil die Compose-Dateien und das `Caddyfile` aus ihm kommen.
- `KIEKMAP_VERSION` nennt die Abbilder, die Compose startet. Ohne den neuen Wert startet es wieder
  die alten, und nichts sagt es.
- `up -d` ersetzt die Container, deren Abbild sich geändert hat, und kehrt zurück. Beim ersten Start
  bringt das Backend das Datenbankschema selbst nach vorn.
- Ein Wappen im Baum des Servers schadet nicht und bewirkt nichts: Das Abbild trägt sein eigenes.

**5. Die Prüfung**, noch auf dem Server:

```bash
docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.web.yml --env-file .env ps
```

Drei Container, alle `Up`, das Backend `healthy`, und die beiden Kiekmap-Abbilder mit der neuen
Version im Tag. Die Version, die das Backend selbst meldet, von überall:

```bash
curl -u museum https://fotos.example.org/api/health
```

curl fragt nach dem Kennwort und muss mit der neuen Version antworten.

**6. Aufräumen**, sobald die neue Version läuft:

```bash
rm -r ~/kiekmap-update
docker image ls 'kiekmap-*'
docker image rm kiekmap-backend:<alte Version> kiekmap-frontend:<alte Version>
```

### Vorher ausprobieren

Mit `KIEKMAP_WEB_DOMAIN=localhost` stellt Caddy ein eigenes Zertifikat aus und braucht weder Domain
noch öffentliche Adresse. Der Browser warnt einmal vor diesem Zertifikat. Das prüft Kennwort und
Wegführung; es prüft nicht das Zertifikat von Let's Encrypt. Auf einem Mac muss die Überlagerung
des Entwicklungsrechners mitkommen, weil es dort kein `/media` gibt:

```bash
docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.mac.yml \
    -f deploy/docker-compose.web.yml --env-file .env up --build
```

---

## Wo die Sicherung liegt

Auf dem Stick im Ordner `kiekmap-backup/`:

```
kiekmap-backup/
  backup.json        Datum, Anzahl, Ortsname
  kiekmap.db        die Angaben, mit VACUUM INTO konsistent herausgeschrieben
  photos/            die Originale, nach ihrem Hash abgelegt
  thumbs/            die Vorschaubilder
  region.json        Kartenausschnitt
  places.json        Ortsverzeichnis
```

Ordner statt Archiv: Eine abgebrochene Sicherung ist so teilweise brauchbar statt komplett
wertlos, und die Bilder lassen sich an jedem Rechner ansehen.

Nach einer **Wiederherstellung** liegt der bisherige Stand unter `data/before-<Datum>/` — inklusive
Datenbank und Write-Ahead-Log. Er wird nie automatisch gelöscht. Wenn feststeht, dass alles stimmt:

```bash
rm -rf data/before-2026-07-29-1115
```

Das ist der einzige Ort, an dem die SD-Karte unbemerkt volllaufen kann.

**Eine Wiederherstellung und ein schreibender Befehl schließen einander aus.** `import`, `scan`,
`places`, `seed-load` und `empty` halten während ihres Laufs eine Sperre auf `data/kiekmap.lock`.
Eine Wiederherstellung, die in dieser Zeit beginnt, bricht sofort ab, verändert nichts und meldet
das im Admin-Bereich. Ein Befehl, der während einer Wiederherstellung beginnt, schreibt nichts und
endet mit `A restore is running`. `stats`, `duplicates`, `pin` und `seed-export` lesen nur und
laufen jederzeit. Die Sperre erreicht auch Befehle über `docker compose exec` oder `run --rm`, weil
jeder Container dasselbe `data/` sieht. Der Kernel gibt sie frei, wenn ein Prozess endet, auch nach
einem Absturz oder Stromausfall; die Datei selbst bleibt liegen und darf nicht gelöscht werden.
**Nicht auf dem Mac mit `make prod-mac`:** Die Dateifreigabe von Docker Desktop übergeht die
Sperre, sogar innerhalb eines Containers.

Das Gerät für einen anderen Ort einrichten: [adaption.de.md](adaption.de.md).
