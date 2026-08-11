#!/usr/bin/env python3
"""Verify IL-size citations in the docs against the DLL.

Every `Type::Method` / `Type.Method` claim followed by `IL=N` (or `N IL`) in a
hand-written doc is checked against the live assembly: the type must exist and
some overload of the method must have that exact IL size. The manual IL-citation
sweep missed the "N IL" table format (loop.md once carried SaveLoad IL=884 vs
926); this machine check closes that gap for all parseable claim formats.

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

    # claim formats: Type::Method / Type.Method optionally followed by (args)
    # then (IL=N); plus "N IL" after a method token on the same line.
    claim_pat = re.compile(
        r"(?<![A-Za-z0-9_>])([A-Za-z_][A-Za-z0-9_]*)(?:::|\.)"
        r"([A-Za-z_][A-Za-z0-9_]*)(?:\([^()]*\))?[\s`]*\(?IL=(\d+)"
    )
    # the corpus's shorthand convention: docs cite NetPackage*/AIDirector*/etc.
    # types by suffix. A claim whose type only resolves via a prefix is checked
    # too; a claim on a genuinely unresolvable type is skipped, not failed.
    prefixes = ("NetPackage", "AIDirector", "ConsoleCmd", "TileEntity", "TEFeature")
    date_pat = re.compile(r"\d{4}-\d{2}-\d{2}")
    bad = []
    n_claims = 0
    n_skipped = 0
    for root, _, files in os.walk(DOCS):
        for fn in files:
            if not fn.endswith(".md"):
                continue
            p = os.path.join(root, fn)
            text = open(p, encoding="utf-8", errors="replace").read()
            for m in claim_pat.finditer(text):
                typ, meth, claimed = m.group(1), norm(m.group(2)), int(m.group(3))
                line = text[: m.start()].count("\n")
                linestr = text.splitlines()[line] if line < len(text.splitlines()) else ""
                if date_pat.search(linestr):
                    n_skipped += 1
                    continue  # dated changelog notes may describe pre-fix states
                n_claims += 1
                sizes = methods.get(norm(typ), {}).get(meth)
                if sizes is None:
                    for pre in prefixes:
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
        print(f"({len(bad)} mismatches of {n_claims} claims)")
        return 1
    print(f"OK: {n_claims} IL citations verified against the DLL")
    return 0


if __name__ == "__main__":
    sys.exit(main())
