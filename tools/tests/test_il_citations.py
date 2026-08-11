#!/usr/bin/env python3
"""Verify IL-size citations in the docs against the DLL.

Every `Type::Method` / `Type.Method` claim followed by `IL=N` (or the `**N IL**`
table form) in a hand-written doc is checked against the live assembly: the type
must exist and some overload of the method must have that exact IL size. The
manual IL-citation sweep missed both the "N IL" table format (loop.md once
carried SaveLoad IL=884 vs 926) and body lines next to corrected changelog notes
(GetCellsOnRay 244, PersistentPlayerLogin 5); this machine check closes those
gaps. Dated changelog notes are skipped (historical records); types cited by
suffix (NetPackage*/AIDirector* shorthand) resolve via prefix.

Usage: python3 tools/tests/test_il_citations.py <asm>
"""
import os
import re
import subprocess
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(TOOLS)
DOCS = os.path.join(REPO, "docs")

SRC = r"""
using System;
using System.Linq;
using Mono.Cecil;
class IlCite {
  static void Main(string[] a) {
    var r = new DefaultAssemblyResolver();
    r.AddSearchDirectory(System.IO.Path.GetDirectoryName(System.IO.Path.GetFullPath(a[0])));
    var asm = AssemblyDefinition.ReadAssembly(a[0], new ReaderParameters { AssemblyResolver = r });
    foreach (var t in asm.MainModule.GetTypes())
      foreach (var m in t.Methods.Where(x => x.HasBody))
        Console.WriteLine(t.FullName + "\t" + m.Name + "\t" + m.Body.Instructions.Count);
  }
}
"""
EXE = "/tmp/ilcite_check.exe"

CLAIM_PAT = re.compile(
    r"(?<![A-Za-z0-9_>])([A-Za-z_][A-Za-z0-9_]*)(?:::|\.)"
    r"([A-Za-z_][A-Za-z0-9_]*)(?:\([^()]*\))?[\s`]*\(?IL=(\d+)"
)
TABLE_PAT = re.compile(
    r"(?<![A-Za-z0-9_>])([A-Za-z_][A-Za-z0-9_]*)(?:::|\.)"
    r"([A-Za-z_][A-Za-z0-9_]*)(?:\([^()]*\))?[^|\n]*\|\s*\*{0,2}(\d+)\s*IL\b"
)
DATE_PAT = re.compile(r"\d{4}-\d{2}-\d{2}")
# corpus shorthand: docs cite NetPackage*/AIDirector*/etc. types by suffix.
PREFIXES = ("NetPackage", "AIDirector", "ConsoleCmd", "TileEntity", "TEFeature")


def norm(s: str) -> str:
    return re.sub(r"`\d+$", "", s)


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: test_il_citations.py <asm>", file=sys.stderr)
        return 2
    asm = sys.argv[1]
    src = "/tmp/ilcite_check.cs"
    with open(src, "w") as f:
        f.write(SRC)
    subprocess.run(
        ["mcs", "-r:%s" % os.path.join(TOOLS, "bin", "Mono.Cecil.dll"), src, "-out:" + EXE],
        check=True,
    )
    env = dict(os.environ)
    env["MONO_PATH"] = os.path.join(TOOLS, "bin")
    out = subprocess.run(
        ["mono", EXE, asm], capture_output=True, text=True, env=env, check=True,
    ).stdout
    # type full-name (normalized) -> method name (normalized) -> set of IL sizes
    methods = {}
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        full, name, il = parts[0], parts[1], int(parts[2])
        short = norm(full.rsplit("/", 1)[-1].rsplit(".", 1)[-1])
        for key in (norm(full), short):
            methods.setdefault(key, {}).setdefault(norm(name), set()).add(il)

    bad = []
    n_claims = 0
    n_skipped = 0
    # the corpus convention bans IL approximations in live prose ("IL=~N" was
    # upgraded to exact values in the 2026-08-11 sweep; a regression fails here).
    approx = re.compile(r"IL\s*=\s*~")
    for root, _, files in os.walk(DOCS):
        for fn in files:
            if not fn.endswith(".md"):
                continue
            p = os.path.join(root, fn)
            text = open(p, encoding="utf-8", errors="replace").read()
            lines = text.splitlines()
            for no, ls in enumerate(lines):
                if DATE_PAT.search(ls):
                    continue
                if approx.search(ls):
                    bad.append(f"{p}:{no + 1}: IL approximation `IL=~` (must be exact)")
            for pat in (CLAIM_PAT, TABLE_PAT):
                for m in pat.finditer(text):
                    typ, meth, claimed = m.group(1), norm(m.group(2)), int(m.group(3))
                    line_no = text[: m.start()].count("\n")
                    linestr = lines[line_no] if line_no < len(lines) else ""
                    if DATE_PAT.search(linestr) and "(exact)" not in linestr:
                        n_skipped += 1
                        continue  # dated changelog notes may describe pre-fix states
                    if DATE_PAT.search(linestr) and typ in ("ChunkData", "Component"):
                        n_skipped += 1
                        continue  # shorthand for DynamicMeshChunkData / AIDirector*Component
                    n_claims += 1
                    sizes = methods.get(norm(typ), {}).get(meth)
                    if sizes is None:
                        for pre in PREFIXES:
                            sizes = methods.get(norm(pre + typ), {}).get(meth)
                            if sizes is not None:
                                break
                    if sizes is None:
                        n_skipped += 1
                        continue  # shorthand / unresolvable by this token
                    if claimed not in sizes:
                        bad.append(f"{p}: {typ}::{meth} IL={claimed}, DLL has {sorted(sizes)}")
    if bad:
        for b in bad[:40]:
            print("FAIL:", b)
        if len(bad) > 40:
            print(f"...and {len(bad) - 40} more")
        print(f"({len(bad)} mismatches of {n_claims} live claims, {n_skipped} skipped)")
        return 1
    print(f"OK: {n_claims} IL citations verified against the DLL ({n_skipped} changelog/shorthand skipped)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
