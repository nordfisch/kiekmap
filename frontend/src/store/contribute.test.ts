import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("../api/client", () => ({
  fetchTask: vi.fn(),
  postLocation: vi.fn(),
  postDate: vi.fn(),
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
  postLocation,
} from "../api/client";
import { useContribute } from "./contribute";
import { useKiosk } from "./kiosk";

const geholt = vi.mocked(fetchTask);
const fotosGeholt = vi.mocked(fetchPhotos);
const histogrammGeholt = vi.mocked(fetchHistogram);
const ortGesendet = vi.mocked(postLocation);

function aufgabe(need: Need, fotoId: number | null, offen = 3): Task {
  return {
    need,
    open_count: fotoId === null ? 0 : offen,
    photo: fotoId === null ? null : ({ id: fotoId, title: `Foto ${fotoId}` } as PhotoDetail),
  };
}

/** Antwortet je nach gefragter Art -- so wie der Bestand im Museum es tut. */
function bestand(nachOrt: Task, nachJahr: Task) {
  geholt.mockImplementation((need: Need) =>
    Promise.resolve(need === "location" ? nachOrt : nachJahr),
  );
}

beforeEach(() => {
  geholt.mockReset();
  fotosGeholt.mockReset().mockResolvedValue({ photos: [], total: 0, truncated: false });
  histogrammGeholt
    .mockReset()
    .mockResolvedValue({ decades: [], undated: 0, collection_from: null, collection_to: null });
  ortGesendet.mockReset().mockResolvedValue({ id: 1 } as PhotoDetail);

  useContribute.setState({
    need: "location",
    task: null,
    loading: false,
    error: null,
    thanks: null,
    skipped: [],
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

    // Die Liste gilt für beide Fragearten: einmal weggetippt ist weggetippt.
    expect(useContribute.getState().skipped).toEqual([7]);
    expect(geholt).toHaveBeenCalledWith("date", [7], expect.anything());
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

  it("meldet erst Vollständigkeit, wenn beide Seiten leer sind", async () => {
    bestand(aufgabe("location", null), aufgabe("date", null));
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

describe("Die Karte beim Verorten", () => {
  beforeEach(() => {
    useKiosk.setState({ focus: null, rangeBefore: null, bbox: [9.6, 53.57, 9.75, 53.67] });
  });

  it("holt bei einem Treffer der Ortssuche heran", () => {
    // Der Besucher hat den Punkt nicht selbst gesetzt -- er will sehen, wo er gelandet ist.
    useContribute.getState().setPin({ lat: 53.62, lon: 9.676 }, { label: "Mühlenweg" });

    expect(useKiosk.getState().focus).not.toBeNull();
    expect(useKiosk.getState().focus?.lat).toBe(53.62);
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

  it("laesst den Zeitraum in Ruhe, solange nichts beigetragen ist", () => {
    useKiosk.setState({ timeRange: { from: 1950, to: 1959 }, fullRange: { from: 1920, to: 2019 } });

    useContribute.getState().setPin({ lat: 53.62, lon: 9.676 }, { label: "Mühlenweg" });

    expect(useKiosk.getState().timeRange).toEqual({ from: 1950, to: 1959 });
    expect(useKiosk.getState().rangeBefore).toBeNull();
  });
});
