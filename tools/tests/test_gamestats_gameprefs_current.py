#!/usr/bin/env python3
"""Guard the gamestats-gameprefs index tables against the DLL's enum members.

docs/inventories/gamestats-gameprefs.md tables every EnumGameStats (82) and
EnumGamePrefs (317) member by array index. A game patch that adds, renames,
or removes a member without updating the doc fails here (the existing
check_stock_facts gate only pins the member *counts*).

Usage: python3 tools/tests/test_gamestats_gameprefs_current.py <asm>
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOC = os.path.join(REPO, "docs", "inventories", "gamestats-gameprefs.md")
DOCS_DIR = os.path.join(REPO, "docs")
ENUMS = ["EnumGameStats", "EnumGamePrefs", "EnumGameState"]

SRC = r"""
using System;
using System.Linq;
using Mono.Cecil;
class EnumNames {
  static void Main(string[] a) {
    var r = new DefaultAssemblyResolver();
    r.AddSearchDirectory(System.IO.Path.GetDirectoryName(System.IO.Path.GetFullPath(a[0])));
    var asm = AssemblyDefinition.ReadAssembly(a[0], new ReaderParameters { AssemblyResolver = r });
    foreach (var tn in a[1].Split(',')) {
      var t = asm.MainModule.GetTypes().First(x => x.Name == tn);
      var names = t.Fields.Where(f => f.HasConstant)
                   .OrderBy(f => Convert.ToInt64(f.Constant))
                   .Select(f => f.Name + "=" + f.Constant);
      Console.WriteLine(tn + ":" + string.Join(",", names));
    }
  }
}
"""


def table_rows(doc: str, section: str, next_section: str) -> list[str]:
    sec = doc.split("## " + section)[1].split("## " + next_section)[0]
    return [
        m.group(2)
        for m in re.finditer(r"^\| (\d+) \| `([^`]+)`", sec, re.M)
    ]


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: test_gamestats_gameprefs_current.py <asm>", file=sys.stderr)
        return 2
    asm = sys.argv[1]
    out = _common.run_probe(
        _common.compile_probe(SRC, "enumnames_check"), asm, ",".join(ENUMS)
    )
    dll = {}
    for line in out.splitlines():
        name, _, members = line.partition(":")
        dll[name] = members.split(",") if members else []

    doc = open(DOC, encoding="utf-8").read()
    bad = []
    # the hand-annotated EnumGameState values in the doc's note must match the DLL
    want_state = ["Off=-1", "Loading=0", "Running=1", "Over=2"]
    have_state = [m for m in dll.get("EnumGameState", []) if "=" in m]
    if have_state != want_state:
        bad.append(f"EnumGameState values: DLL {have_state} != doc note {want_state}")
    note = re.search(r"EnumGameState\` \((.*?)\)", doc, re.S)
    note_ws = re.sub(r"\s+", " ", note.group(1)).strip() if note else ""
    want_ws = ", ".join(want_state)
    if not note or note_ws != want_ws:
        bad.append(f"EnumGameState note in doc: `{note_ws or 'missing'}` != `{want_ws}`")
    for i, enum in enumerate(ENUMS[:2]):
        nxt = ENUMS[i + 1] if i + 1 < 2 else "ZZZ_NO_SUCH_SECTION"
        rows = table_rows(doc, enum, nxt)
        dll_names = [m.split("=")[0] for m in dll[enum]]
        if rows != dll_names:
            # report first divergence compactly
            for j, (a, b) in enumerate(zip(rows, dll_names, strict=False)):
                if a != b:
                    bad.append(f"{enum}[{j}]: doc `{a}` != DLL `{b}`")
                    break
            if len(rows) != len(dll_names):
                bad.append(f"{enum}: doc rows {len(rows)} != DLL members {len(dll[enum])}")
            if not bad or all(enum not in b for b in bad):
                bad.append(f"{enum}: tables diverge from the DLL (regenerate the doc)")
    # the note + tables above; also: every `GameStats[N]` / `GamePrefs.Get*(N)`
    # index cited anywhere in the corpus must be in enum range (82 / 317)
    n_state = len(dll["EnumGameStats"])
    n_prefs = len(dll["EnumGamePrefs"])
    stats_rows = table_rows(doc, "EnumGameStats", "EnumGamePrefs")
    for root, _dirs, files in os.walk(DOCS_DIR):
        for fn in files:
            if not fn.endswith(".md"):
                continue
            txt = open(os.path.join(root, fn), encoding="utf-8", errors="replace").read()
            for m in re.finditer(r"GameStats\[(\d+)\]", txt):
                if int(m.group(1)) >= n_state:
                    bad.append(f"{fn}: GameStats[{m.group(1)}] out of range (< {n_state})")
            # named citations (GameStats[N] (Name) / GameStats[N] Name) must match
            # the table; parsed once below the loop, not per citation
            for m in re.finditer(r"GameStats\[(\d+)\]\s*\(?`?([A-Za-z][A-Za-z0-9_]*)", txt):
                idx, name = int(m.group(1)), m.group(2)
                if idx < n_state:
                    rows_i = stats_rows
                    if idx < len(rows_i) and rows_i[idx] != name and name not in ("GameState", "GameModeId"):
                        bad.append(f"{fn}: GameStats[{idx}] named `{name}`, table says `{rows_i[idx]}`")
            for m in re.finditer(r"(?:GetInt|GetFloat|GetBool)\((\d+)\)", txt):
                if int(m.group(1)) >= n_prefs:
                    bad.append(f"{fn}: GamePrefs index {m.group(1)} out of range (< {n_prefs})")
    if bad:
        for b in bad:
            print("FAIL:", b)
        return 1
    print(f"OK: {ENUMS[0]} ({len(dll[ENUMS[0]])}) + {ENUMS[1]} ({len(dll[ENUMS[1]])}) tables match the DLL; cited indices in range")
    return 0


if __name__ == "__main__":
    sys.exit(main())
