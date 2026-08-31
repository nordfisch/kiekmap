# Sicherheit

## Was dieses Gerät ist

Ein Kiosk, der **offline** in einem Museumsraum steht. Er bietet keinen Dienst im Netz an: Der Pi
hängt an keinem Internetanschluss, die Karte liegt als Datei auf dem Gerät, und es gibt keine
Anmeldung ausser einer PIN vor dem Verwaltungsbereich. Das prägt, was hier eine Schwachstelle ist
und was nicht.

## Was ausdrücklich so gewollt ist

Das ist kein Fund, sondern der Entwurf:

- **Die Besucheransicht kennt keine Anmeldung.** Wer vor dem Gerät steht, darf Fotos ansehen und
  Angaben ergänzen. Genau dafür ist es aufgestellt.
- **Beiträge werden ungeprüft übernommen**, aber nur in leere Felder; kuratierte Angaben sind
  unantastbar, und jede Änderung steht im Änderungsprotokoll und ist zurücknehmbar.
- **Es gibt keine Ratenbegrenzung am Beitragsweg.** In einem Raum mit Aufsicht ist das folgenlos.
  Für einen Betrieb im Netz ist es das nicht — deshalb liegt dieser Fall als
  [Punkt 21](https://github.com/nordfisch/kiekmap/issues/22), mit einer Anmeldung vor der ganzen Anwendung als Weg.
- **Der Fotobestand ist nicht verschlüsselt.** Er liegt als Dateien auf dem Gerät und auf dem
  Sicherungsstick. Ein Museum, das das anders braucht, verschlüsselt den Datenträger.

## Was eine Meldung wert ist

Alles, was jemand **vor dem Gerät** oder **mit einem USB-Stick** erreichen kann und was nicht
oben steht: ein Weg an der PIN vorbei, ein Import, der aus dem vorgesehenen Verzeichnis
ausbricht, eine Wiederherstellung, die Dateien ausserhalb des Bestands anfasst, ein Beitrag, der
kuratierte Angaben überschreibt. Ebenso alles, was aus einer der Abhängigkeiten mitgeliefert
kommt.

Wer das Gerät ins Netz stellt, tut das ausserhalb des vorgesehenen Betriebs — dann gelten die
offenen Punkte oben, und sie sind bekannt.

## Melden

**Nicht als öffentliche Meldung.** Über die private Meldung bei GitHub — im Reiter „Security" des
Repos, „Report a vulnerability". Sie geht nur an den Betreuer und ist erst sichtbar, wenn die
Sache behoben ist.

Es gibt einen Betreuer, nebenher. Eine Antwortzeit ist nicht zugesagt; eine Meldung wird
gelesen. Was behoben wird, steht danach im [CHANGELOG](CHANGELOG.md) und, mit dem Warum, in
[history.md](docs/history.md).

## Welche Fassung gepflegt wird

Nur die jeweils letzte. Es gibt keine Zweige für ältere Stände.
