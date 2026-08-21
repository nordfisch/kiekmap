// SPDX-FileCopyrightText: 2026 Kalle Erlhoff
// SPDX-License-Identifier: Apache-2.0

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

// `importOriginal` statt einer vollständigen Attrappe, und zwar wegen genau einer Zeile: `NEEDS`
// ist die Rangfolge der drei Fragen. Als abgeschriebene Liste im Test wäre sie eine zweite
// Wahrheit — die Reihenfolge in `client.ts` ließe sich vertauschen, ohne dass ein Test es merkt.
// Nachgeprüft: mit einer Kopie fiel bei vertauschter Reihenfolge keiner.
vi.mock("../api/client", async (importOriginal) => ({
  ...(await importOriginal<typeof import("../api/client")>()),
  fetchTask: vi.fn(),
  postLocation: vi.fn(),
  postDate: vi.fn(),
  postHouseNumber: vi.fn(),
  // Der Kiosk-Store haengt an derselben Schicht -- ein Beitrag laesst ihn nachladen.
  fetchPhotos: vi.fn(),
  fetchHistogram: vi.fn(),
}));

import {
  type Need,
  type PhotoDetail,
  type Task,
  fetchHistogram,
  fetchPhotos,
  fetchTask,
  postDate,
  postHouseNumber,
  postLocation,
} from "../api/client";
import { t } from "../text/de";
import { useContribute } from "./contribute";
import { useKiosk } from "./kiosk";

const geholt = vi.mocked(fetchTask);
const fotosGeholt = vi.mocked(fetchPhotos);
const histogrammGeholt = vi.mocked(fetchHistogram);
const ortGesendet = vi.mocked(postLocation);
const jahrGesendet = vi.mocked(postDate);
const nummerGesendet = vi.mocked(postHouseNumber);

function aufgabe(need: Need, fotoId: number | null, offen = 3, andere = 3): Task {
  return {
    need,
    open_count: fotoId === null ? 0 : offen,
    open_other: andere,
    photo: fotoId === null ? null : ({ id: fotoId, title: `Foto ${fotoId}` } as PhotoDetail),
  };
}

/**
 * Antwortet je nach gefragter Art -- so wie der Bestand im Museum es tut.
 *
 * Die Nachschärf-Frage ist standardmäßig leer. Wer sie prüfen will, gibt sie ausdrücklich an —
 * sonst prüfte jeder Test nebenbei eine Frage, um die es ihm gar nicht geht.
 */
function bestand(nachOrt: Task, nachJahr: Task, nachNummer = aufgabe("housenumber", null)) {
  geholt.mockImplementation((need: Need) =>
    Promise.resolve(need === "location" ? nachOrt : need === "date" ? nachJahr : nachNummer),
  );
}

beforeEach(() => {
  geholt.mockReset();
  fotosGeholt.mockReset().mockResolvedValue({ photos: [], total: 0, truncated: false });
  histogrammGeholt.mockReset().mockResolvedValue({
    bars: [],
    step: 1,
    undated: 0,
    collection_from: null,
    collection_to: null,
  });
  ortGesendet.mockReset().mockResolvedValue({ id: 1 } as PhotoDetail);
  jahrGesendet.mockReset().mockResolvedValue({ id: 1, needs_date: false } as PhotoDetail);
  nummerGesendet.mockReset().mockResolvedValue({ id: 1, place_name: "Am Kamp 12" } as PhotoDetail);

  useContribute.setState({
    need: "location",
    task: null,
    loading: false,
    error: null,
    thanks: null,
    skipped: [],
    pickingOnMap: false,
    pin: null,
    pinLabel: null,
  });
  // Ein Ausschnitt muss stehen, sonst gaebe es nichts nachzuladen.
  useKiosk.setState({ bbox: [9.6, 53.57, 9.75, 53.67] });
});

describe("„Weiß ich nicht“", () => {
  it("wechselt die Frage statt nur das Foto", async () => {
    // Wer einen Ort nicht erkennt, weiß vielleicht trotzdem das Jahrzehnt. Dieselbe Frage noch
    // einmal ist der Grund, warum jemand nach drei Bildern aufhört.
    bestand(aufgabe("location", 1), aufgabe("date", 2));
    useContribute.setState({ need: "location", task: aufgabe("location", 1) });

    useContribute.getState().skip();
    await vi.waitFor(() => expect(useContribute.getState().need).toBe("date"));

    expect(useContribute.getState().task?.photo?.id).toBe(2);
  });

  it("wechselt auch wieder zurück", async () => {
    bestand(aufgabe("location", 1), aufgabe("date", 2));
    useContribute.setState({ need: "date", task: aufgabe("date", 2) });

    useContribute.getState().skip();
    await vi.waitFor(() => expect(useContribute.getState().need).toBe("location"));
  });

  it("merkt sich das weggetippte Foto", async () => {
    bestand(aufgabe("location", 1), aufgabe("date", 2));
    useContribute.setState({ need: "location", task: aufgabe("location", 7) });

    useContribute.getState().skip();
    await vi.waitFor(() => expect(useContribute.getState().need).toBe("date"));

    // Die Liste gilt für alle Fragearten: einmal weggetippt ist weggetippt. Geprüft über *jeden*
    // Aufruf statt über einen benannten — welche Frage als nächste drankommt, sagt die Rangfolge,
    // und die ist hier nicht das Thema.
    expect(useContribute.getState().skipped).toEqual([7]);
    for (const [, uebersprungen] of geholt.mock.calls) {
      expect(uebersprungen).toEqual([7]);
    }
  });
});

describe("Rückfall, wenn eine Frage leerläuft", () => {
  it("bleibt bei der bisherigen Frage, wenn die andere nichts mehr hat", async () => {
    // Der Fall, der den Wechsel sonst kaputtmacht: In einer Sammlung, in der jedes Foto verortet
    // ist, aber die Hälfte kein Jahr hat, stünde sonst „alles vollständig" auf dem Schirm --
    // während Hunderte Fotos auf eine Jahreszahl warten.
    bestand(aufgabe("location", 5), aufgabe("date", null));
    useContribute.setState({ need: "location", task: aufgabe("location", 4) });

    useContribute.getState().skip();
    await vi.waitFor(() => expect(useContribute.getState().task?.photo?.id).toBe(5));

    expect(useContribute.getState().need).toBe("location");
  });

  it("meldet erst Vollständigkeit, wenn alle drei Fragen leer sind", async () => {
    // Der stille Fehler wäre, „alles vollständig" zu melden, während noch nachzuschärfen ist.
    bestand(aufgabe("location", null), aufgabe("date", null), aufgabe("housenumber", null));
    useContribute.setState({ need: "location", task: aufgabe("location", 1) });

    useContribute.getState().skip();
    await vi.waitFor(() => expect(useContribute.getState().loading).toBe(false));

    expect(useContribute.getState().task?.photo).toBeNull();
  });

  it("greift auch beim ersten Laden", async () => {
    // Eine Sammlung, in der noch nichts datiert ist: die Startfrage muss trotzdem etwas zeigen.
    bestand(aufgabe("location", null), aufgabe("date", 9));

    await useContribute.getState().load("location");

    expect(useContribute.getState().need).toBe("date");
    expect(useContribute.getState().task?.photo?.id).toBe(9);
  });
});

describe("Die Rangfolge der drei Fragen", () => {
  it("kommt zum Nachschaerfen, wenn nach dem Ort nichts mehr offen ist", async () => {
    /**
     * Ein Foto irgendwohin zu setzen ist mehr wert, als eines von der Straßenmitte an sein Haus zu
     * rücken — und diese Rangfolge steckt allein in der Reihenfolge von `NEEDS`, nicht in einer
     * Fallunterscheidung.
     */
    bestand(aufgabe("location", null), aufgabe("date", null), aufgabe("housenumber", 12));

    await useContribute.getState().load("location");

    expect(useContribute.getState().need).toBe("housenumber");
    expect(useContribute.getState().task?.photo?.id).toBe(12);
  });

  it("nimmt die Hausnummer vor dem Jahr, wenn beide etwas haetten", async () => {
    /**
     * Der Test, der die Reihenfolge in `NEEDS` wirklich prüft: Beide Fragen könnten liefern, und
     * nur die Position im Tupel entscheidet. Ohne ihn ließe sich „housenumber" und „date"
     * vertauschen, ohne dass ein Test es merkte — nachgeprüft, es fiel keiner.
     *
     * Dass die Hausnummer vorn steht, ist am 11. August 2026 aus einer Zahl entschieden worden
     * und nicht aus dem Gefühl: Ein Jahr ist mehr wert als eine Hausnummer, aber im Bestand
     * stehen 673 undatierte Fotos gegen 71 nachzuschärfende. Hinter dem Jahr wäre die dritte
     * Frage nie erreicht worden — siehe `services/needs.py`.
     */
    bestand(aufgabe("location", null), aufgabe("date", 8), aufgabe("housenumber", 12));

    await useContribute.getState().load("location");

    expect(useContribute.getState().need).toBe("housenumber");
    expect(useContribute.getState().task?.photo?.id).toBe(12);
  });

  it("laesst das Nachschaerfen liegen, solange ein Foto ohne Ort dasteht", async () => {
    // Die Gegenrichtung: Es genügt *ein* unverortetes Foto, damit die feinere Frage wartet.
    bestand(aufgabe("location", 3), aufgabe("date", null), aufgabe("housenumber", 12));

    await useContribute.getState().load("location");

    expect(useContribute.getState().need).toBe("location");
  });

  it("erreicht das Nachschaerfen von der Jahresfrage aus", async () => {
    // Die Ausnahme gilt nur für die Frage, die nachgeschärft wird — von „Wann war das?" aus ist
    // der Weg offen, sonst wäre die dritte Frage aus dem Bereich heraus nie erreichbar.
    bestand(aufgabe("location", null), aufgabe("date", null), aufgabe("housenumber", 12));
    useContribute.setState({ need: "date", task: aufgabe("date", 8) });

    useContribute.getState().skip();
    await vi.waitFor(() => expect(useContribute.getState().need).toBe("housenumber"));

    expect(useContribute.getState().task?.photo?.id).toBe(12);
  });
});

describe("Die scharfe Karte faellt zurueck", () => {
  /**
   * Der Kartentipp ist nur nach ausdruecklicher Ansage scharf — und diese Ansage gilt fuer
   * *dieses* Foto. Ueberlebte sie den Wechsel, verortete der naechste Tipp ein Foto, das der
   * Besucher noch gar nicht angesehen hat.
   */
  beforeEach(() => {
    bestand(aufgabe("location", 5), aufgabe("date", 6));
  });

  it("beim naechsten Foto", async () => {
    useContribute.setState({ need: "location", task: aufgabe("location", 4), pickingOnMap: true });

    useContribute.getState().skip();
    await vi.waitFor(() => expect(useContribute.getState().loading).toBe(false));

    expect(useContribute.getState().pickingOnMap).toBe(false);
  });

  it("auch dann, wenn die Frage dieselbe bleibt", async () => {
    /**
     * Der Weg, der die Komponente stehen laesst: Hat die andere Frage nichts mehr, faellt
     * ``load`` auf die urspruengliche zurueck. ``need`` bleibt „location", ``LocationTask``
     * bleibt montiert — ein ``useState`` in der Komponente wuerde hier nicht zurueckfallen.
     * Genau deshalb wohnt der Schalter im Store.
     */
    bestand(aufgabe("location", 5), aufgabe("date", null));
    useContribute.setState({ need: "location", task: aufgabe("location", 4), pickingOnMap: true });

    useContribute.getState().skip();
    await vi.waitFor(() => expect(useContribute.getState().task?.photo?.id).toBe(5));

    expect(useContribute.getState().need).toBe("location");
    expect(useContribute.getState().pickingOnMap).toBe(false);
  });

  it("bei jedem Laden, nicht nur auf den beiden bequemen Wegen", async () => {
    /**
     * ``skip`` und ``contribute`` setzen selbst zurueck — deshalb faellt es nicht auf, wenn
     * ``load`` es nicht taete. ``load`` ist aber die Stelle, die *jeden* Fotowechsel sieht, auch
     * den aus der Detailansicht und den beim ersten Aufbau des Bereichs. Dieser Test deckt genau
     * die Zeile, die den beiden anderen sonst nur hinterherraeumt.
     */
    useContribute.setState({ need: "location", task: aufgabe("location", 4), pickingOnMap: true });

    await useContribute.getState().load();

    expect(useContribute.getState().pickingOnMap).toBe(false);
  });

  it("nach einem Beitrag", async () => {
    useContribute.setState({ need: "location", task: aufgabe("location", 4), pickingOnMap: true });
    useContribute.getState().setPin({ lat: 53.62, lon: 9.676 });

    await useContribute.getState().submitLocation();

    expect(useContribute.getState().pickingOnMap).toBe(false);
  });

  it("ist von vornherein aus", () => {
    // Wer nur schauen will, soll die Frage nicht versehentlich beantworten.
    expect(useContribute.getInitialState().pickingOnMap).toBe(false);
  });
});

describe("Karte und Zeitleiste nach einem Beitrag", () => {
  beforeEach(() => {
    bestand(aufgabe("location", 2), aufgabe("date", 3));
    useContribute.setState({
      need: "location",
      task: aufgabe("location", 1),
      pin: { lat: 53.62, lon: 9.676 },
    });
  });

  it("laedt beide nach, sobald ein Beitrag angekommen ist", async () => {
    // Der Dank verspricht „Das Foto ist jetzt auf der Karte". Ohne dieses Nachladen wurde das
    // erst wahr, wenn jemand die Karte verschob -- also gerade bei den aelteren Besuchern, fuer
    // die der Bereich gebaut ist, gar nicht.
    await useContribute.getState().submitLocation();

    expect(fotosGeholt).toHaveBeenCalled();
    // Das Histogramm gehoert dazu: ein verortetes Foto wandert aus "ohne Ort" heraus, ein
    // datiertes aus "ohne Jahr" in einen Jahrzehnt-Balken.
    expect(histogrammGeholt).toHaveBeenCalled();
  });

  it("laedt nicht nach, wenn der Beitrag abgelehnt wurde", async () => {
    // Haeufigster Fall: jemand anders war schneller (HTTP 409). Dann hat sich nichts geaendert,
    // und ein Nachladen waere nur Last auf dem Pi.
    ortGesendet.mockRejectedValue(new Error("Dieses Foto hat inzwischen schon eine Angabe."));

    await useContribute.getState().submitLocation();

    expect(useContribute.getState().error).toContain("inzwischen");
    expect(fotosGeholt).not.toHaveBeenCalled();
  });

  it("laedt nicht nach, solange kein Ausschnitt bekannt ist", async () => {
    // Vor dem ersten Kartenaufbau gibt es keine bbox -- dann gibt es auch nichts abzufragen.
    useKiosk.setState({ bbox: null });

    await useContribute.getState().submitLocation();

    expect(fotosGeholt).not.toHaveBeenCalled();
  });
});

describe("Nach einem Beitrag: dasselbe Foto, die andere Frage", () => {
  /**
   * Ein frisch eingelesener Scan hat oft weder Ort noch Jahr — im Museumsbestand sind das 673
   * Fotos ohne Jahr und 77 ohne Ort. Welche Frage zuerst kommt, entscheidet der Zufall.
   */
  const datiertOhneOrt = {
    id: 1,
    lat: null,
    lon: null,
    needs_location: true,
    needs_date: false,
  } as PhotoDetail;

  const verortetOhneJahr = {
    id: 1,
    lat: 53.62,
    lon: 9.676,
    needs_location: false,
    needs_date: true,
  } as PhotoDetail;

  const vollstaendig = {
    id: 1,
    lat: 53.62,
    lon: 9.676,
    needs_location: false,
    needs_date: false,
  } as PhotoDetail;

  beforeEach(() => {
    vi.useFakeTimers();
    // Die Aufgaben, die der Bestand von sich aus liefern würde: Foto 2 und Foto 3. Kommt statt
    // ihrer die 1, hat die Kette gegriffen.
    bestand(aufgabe("location", 2), aufgabe("date", 3));
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("dankt ohne Versprechen, solange der Ort fehlt", async () => {
    /**
     * Der Fehler, um den es hier geht. „Das Foto ist jetzt auf der Zeitleiste" war eine Zusage,
     * die die Ansicht nicht einlösen kann: Ein Foto ohne Ort steht auf keiner Karte, der Fokus
     * bleibt stehen, und der Besucher liest einen Satz und sieht nichts.
     */
    useContribute.setState({ need: "date", task: aufgabe("date", 1) });
    jahrGesendet.mockResolvedValue(datiertOhneOrt);

    await useContribute.getState().submitDate(1930, "decade");

    expect(useContribute.getState().thanks).not.toContain("Zeitleiste");
    expect(useContribute.getState().thanks).toBe(t.help.thanksAsk.location);
  });

  it("legt dasselbe Foto zur Ortsfrage vor, wenn es datiert wurde", async () => {
    // Wer gerade gesagt hat, wann das war, kennt das Foto — und schaut es an. Ein zufälliges
    // anderes vorzulegen verschenkt genau diesen Moment.
    useContribute.setState({ need: "date", task: aufgabe("date", 1) });
    jahrGesendet.mockResolvedValue(datiertOhneOrt);

    await useContribute.getState().submitDate(1930, "decade");
    await vi.advanceTimersByTimeAsync(2200);

    expect(useContribute.getState().need).toBe("location");
    expect(useContribute.getState().task?.photo?.id).toBe(1);
  });

  it("legt dasselbe Foto zur Jahresfrage vor, wenn es verortet wurde", async () => {
    // Dieselbe Regel in die andere Richtung, damit sie eine Regel bleibt und kein Sonderfall.
    useContribute.setState({
      need: "location",
      task: aufgabe("location", 1),
      pin: { lat: 53.62, lon: 9.676 },
    });
    ortGesendet.mockResolvedValue(verortetOhneJahr);

    await useContribute.getState().submitLocation();
    expect(useContribute.getState().thanks).toBe(t.help.thanksAsk.date);

    await vi.advanceTimersByTimeAsync(2200);

    expect(useContribute.getState().need).toBe("date");
    expect(useContribute.getState().task?.photo?.id).toBe(1);
  });

  it("verspricht die Karte erst, wenn das Foto darauf zu sehen ist", async () => {
    // Der alte Satz bleibt — nur dort, wo er stimmt.
    useContribute.setState({
      need: "location",
      task: aufgabe("location", 1),
      pin: { lat: 53.62, lon: 9.676 },
    });
    ortGesendet.mockResolvedValue(vollstaendig);

    await useContribute.getState().submitLocation();

    expect(useContribute.getState().thanks).toBe(t.help.thanks.location);
  });

  it("fragt nach „Reicht so“ nicht sofort nach der Hausnummer", async () => {
    /**
     * Die eine echte Ausnahme von der reinen Rangfolge, und sie haengt am *Beantworten*. Wer
     * gerade „Reicht so — die Straße genügt" gedrückt und den Ort bestätigt hat, hat die Frage
     * nach dem genauen Haus schon beantwortet; sie im selben Atemzug noch einmal zu stellen liest
     * sich, als hätte niemand zugehört.
     *
     * Ohne die `refines`-Zeile führte die Kette hier zu „housenumber", weil nach dem Ort und dem
     * Jahr nichts mehr offen ist.
     */
    bestand(aufgabe("location", null), aufgabe("date", null), aufgabe("housenumber", 12));
    useContribute.setState({
      need: "location",
      task: aufgabe("location", 12),
      pin: { lat: 53.62, lon: 9.676 },
      pinLabel: "Am Kamp",
      pinAccuracy: 150,
    });
    ortGesendet.mockResolvedValue(vollstaendig);

    await useContribute.getState().submitLocation();
    await vi.advanceTimersByTimeAsync(2200);

    expect(useContribute.getState().need).not.toBe("housenumber");
  });

  it("geht zum naechsten Foto, wenn nichts mehr fehlt", async () => {
    // Die Kette muss enden, sonst bekäme der Besucher dasselbe Foto ein zweites Mal vorgelegt.
    useContribute.setState({
      need: "location",
      task: aufgabe("location", 1),
      pin: { lat: 53.62, lon: 9.676 },
    });
    ortGesendet.mockResolvedValue(vollstaendig);

    await useContribute.getState().submitLocation();
    await vi.advanceTimersByTimeAsync(2200);

    expect(useContribute.getState().need).toBe("date");
    expect(useContribute.getState().task?.photo?.id).toBe(3);
  });
});

describe("Die Karte beim Verorten", () => {
  beforeEach(() => {
    useKiosk.setState({ focus: null, rangeBefore: null, bbox: [9.6, 53.57, 9.75, 53.67] });
  });

  it("holt bei einem Treffer der Ortssuche heran", () => {
    // Der Besucher hat den Punkt nicht selbst gesetzt -- er will sehen, wo er gelandet ist.
    useContribute.getState().setPin({ lat: 53.62, lon: 9.676 }, { label: "Mühlenweg" });

    // Der Ausschnitt legt sich um den Punkt -- eine eigene Koordinate traegt der Focus nicht,
    // die Karte liest allein `bounds`.
    const [[west, sued], [ost, nord]] = useKiosk.getState().focus!.bounds;
    expect(53.62).toBeGreaterThan(sued);
    expect(53.62).toBeLessThan(nord);
    expect(9.676).toBeGreaterThan(west);
    expect(9.676).toBeLessThan(ost);
  });

  it("laesst sie bei einem auf die Karte getippten Punkt stehen", () => {
    // Dort hat er gerade gezielt. Eine Karte, die unter dem Finger wegspringt, fuehlt sich an wie
    // ein Verrutschen.
    useContribute.getState().setPin({ lat: 53.62, lon: 9.676 });

    expect(useKiosk.getState().focus).toBeNull();
  });

  it("faehrt zurueck, wenn der Punkt entfernt wird", () => {
    useContribute.getState().setPin({ lat: 53.62, lon: 9.676 }, { label: "Mühlenweg" });
    useContribute.getState().setPin(null);

    expect(useKiosk.getState().focus).toBeNull();
  });

  it("gibt nur der Ortssuche ein Etikett mit", () => {
    // Daran unterscheidet die Hausnummern-Auswahl einen Tipp auf die Karte von ihrem eigenen
    // Treffer: Nur beim eigenen steht ein Etikett. Faellt diese Zusage, bliebe das Knopfraster
    // nach einem Kartentipp stehen und wuerfe den eben gesetzten Punkt beim naechsten Tipp weg.
    useContribute.getState().setPin({ lat: 53.62, lon: 9.676 }, { label: "Mühlenweg" });
    expect(useContribute.getState().pinLabel).toBe("Mühlenweg");

    useContribute.getState().setPin({ lat: 53.63, lon: 9.677 });
    expect(useContribute.getState().pinLabel).toBeNull();
  });

  it("laesst den Zeitraum in Ruhe, solange nichts beigetragen ist", () => {
    useKiosk.setState({ timeRange: { from: 1950, to: 1959 }, fullRange: { from: 1920, to: 2019 } });

    useContribute.getState().setPin({ lat: 53.62, lon: 9.676 }, { label: "Mühlenweg" });

    expect(useKiosk.getState().timeRange).toEqual({ from: 1950, to: 1959 });
    expect(useKiosk.getState().rangeBefore).toBeNull();
  });
});

describe("Aus einem Foto heraus fragen", () => {
  /**
   * Der Weg aus der Detailansicht: Wer ein Foto groß ansieht und dort „Wann war das?" tippt, meint
   * genau dieses Foto. Der Wunsch geht an den Server, der ihn gegen dieselbe Bedingung prüft wie
   * jedes andere Foto — siehe `api/contribute.py`.
   */
  function bestandMitWunsch(nachOrt: Task, nachJahr: Task, gewuenscht?: Task) {
    geholt.mockImplementation((need: Need, _uebersprungen: number[], fotoId?: number | null) => {
      if (fotoId != null && gewuenscht && gewuenscht.need === need) {
        return Promise.resolve(gewuenscht);
      }
      return Promise.resolve(need === "location" ? nachOrt : nachJahr);
    });
  }

  it("stellt das gewuenschte Foto zur gewuenschten Frage", async () => {
    bestandMitWunsch(aufgabe("location", 3), aufgabe("date", 8), aufgabe("date", 42));

    await useContribute.getState().askAbout(42, "date");

    expect(useContribute.getState().need).toBe("date");
    expect(useContribute.getState().task?.photo?.id).toBe(42);
  });

  it("reicht die Foto-Nummer nur bei der gewuenschten Frage weiter", async () => {
    // Der Rückfall gilt einer *anderen* Frage. Ein Wunsch, der dort mitliefe, hiesse: „lege mir
    // dieses Foto zu einer Frage vor, zu der es nichts zu sagen hat."
    bestandMitWunsch(aufgabe("location", 3), aufgabe("date", 8), aufgabe("date", 42));

    await useContribute.getState().askAbout(42, "date");

    expect(geholt).toHaveBeenCalledWith("date", [], 42, expect.anything());
  });

  it("faellt auf die Rangfolge zurueck, wenn das Foto nichts mehr braucht", async () => {
    /**
     * Zwischen dem Tippen und dem Laden kann jemand anders geantwortet haben. Der Server legt dann
     * ein anderes Foto vor — und der Bereich macht weiter, statt mit einer beantworteten Frage
     * dazustehen.
     */
    bestandMitWunsch(aufgabe("location", 3), aufgabe("date", 8));

    await useContribute.getState().askAbout(42, "date");

    expect(useContribute.getState().need).toBe("date");
    expect(useContribute.getState().task?.photo?.id).toBe(8);
  });

  it("geht danach den gewohnten Weg", async () => {
    /**
     * Der Test, der festhält, dass hier **keine** Sonderregel gebaut wurde: Nach der Antwort
     * kommen Dank und Kette wie nach jedem anderen Beitrag. Wer aus einem Foto heraus antwortet,
     * ist im Beitragsbereich gelandet, und dort gehört die nächste Frage hin.
     */
    bestandMitWunsch(aufgabe("location", 3), aufgabe("date", 8), aufgabe("date", 42));
    jahrGesendet.mockResolvedValue({
      id: 42,
      needs_date: false,
      needs_location: true,
    } as PhotoDetail);

    await useContribute.getState().askAbout(42, "date");
    await useContribute.getState().submitDate(1932, "year");

    // Der Dank fragt nach dem, was diesem Foto noch fehlt -- und das ist der Ort.
    expect(useContribute.getState().thanks).toBe(t.help.thanksAsk.location);
  });
});
