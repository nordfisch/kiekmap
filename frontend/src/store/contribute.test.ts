import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("../api/client", () => ({
  fetchTask: vi.fn(),
  postLocation: vi.fn(),
  postDate: vi.fn(),
}));

import { type Need, type PhotoDetail, type Task, fetchTask } from "../api/client";
import { useContribute } from "./contribute";

const geholt = vi.mocked(fetchTask);

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
