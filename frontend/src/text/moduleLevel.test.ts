/**
 * No module reads `t` at module level.
 *
 * The trap this guards, found on a running device on 31 August 2026: the filter buttons of the
 * import log stood in German on an English instance. `const RESULTS = [{ label: t.admin… }]` is
 * evaluated when the module is imported -- and every module is imported before `main.tsx` has
 * asked `/api/config`. The array is then filled once, with the default catalogue, and never
 * looked at again.
 *
 * It fails in the worst way it could: the interface works, the words are wrong, and only somebody
 * reading the screen in the other language notices. `tsc` cannot see it -- both catalogues have
 * the same type.
 *
 * The fix is the same every time: a function instead of a constant. This test is the reason
 * nobody has to remember that.
 *
 * The sources come through `import.meta.glob` rather than `node:fs`, so the check needs no
 * `@types/node` and therefore no dependency of its own.
 */

import ts from "typescript";
import { describe, expect, it } from "vitest";

const SOURCES = import.meta.glob("../**/*.{ts,tsx}", {
  query: "?raw",
  eager: true,
  import: "default",
}) as Record<string, string>;

/** Every `t.…` that is not inside a function -- so it runs while the module is being imported. */
function readsAtModuleLevel(path: string, code: string): string[] {
  const source = ts.createSourceFile(path, code, ts.ScriptTarget.Latest, true);
  const found: string[] = [];

  const visit = (node: ts.Node, insideFunction: boolean): void => {
    const isFunction =
      ts.isFunctionDeclaration(node) ||
      ts.isFunctionExpression(node) ||
      ts.isArrowFunction(node) ||
      ts.isMethodDeclaration(node) ||
      ts.isGetAccessor(node);

    if (
      !insideFunction &&
      ts.isPropertyAccessExpression(node) &&
      ts.isIdentifier(node.expression) &&
      node.expression.text === "t"
    ) {
      const { line } = source.getLineAndCharacterOfPosition(node.getStart());
      found.push(`${path}:${line + 1}`);
    }
    ts.forEachChild(node, (child) => visit(child, insideFunction || isFunction));
  };

  ts.forEachChild(source, (node) => visit(node, false));
  return found;
}

describe("the text catalogue", () => {
  it("is read inside functions only, never while a module is being imported", () => {
    const offenders = Object.entries(SOURCES)
      .filter(([path]) => !path.startsWith("../text/") && !/\.test\.tsx?$/.test(path))
      .flatMap(([path, code]) => readsAtModuleLevel(path, code));

    expect(offenders, "a function instead of a constant -- see the note at the top").toEqual([]);
  });

  it("finds the mistake it is built for", () => {
    /** Without this, an accidentally broken scanner would report "all clear" for ever. */
    const broken = `import { t } from "../text";\nconst LABELS = { a: t.admin.imports.all };\n`;

    expect(readsAtModuleLevel("broken.ts", broken)).toEqual(["broken.ts:2"]);
  });
});
