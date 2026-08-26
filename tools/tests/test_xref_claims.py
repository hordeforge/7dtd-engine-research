#!/usr/bin/env python3
"""Guard `Xref=N` call-site claims in narrative docs against the Xref tool.

docs/*.md (hand-written, excluding docs/inventories/) state call-site counts
in the tight form ``Type.Method (Xref=N)`` / ``Type::Method (Xref=N)``. The
Xref tool (tools/src/Xref.cs, builds to tools/bin/Xref.exe) reports every
call/callvirt/newobj/ldftn site attributed to its enclosing method. A doc
claim that drifts from the assembly (a patch adds or removes a caller, or a
doc line is copy-edited into a wrong count) fails here.

Supported claim grammar (the gap between the method name and the
parenthetical may not contain backticks or '(' so the regex cannot jump
across a later method mention):

    `Type.Method` <gap> (Xref=N)
    `Type::Method` <gap> (Xref=N)

Field-access claims are not supported (no (Xref=...) field form in the docs);
use the --field flag of Xref.exe and write the claim as (field Xref=N) if a
field claim is ever added.

All claims are verified with ONE `Xref <asm> --batch` invocation (a single
assembly pass), not one process per claim.

Usage: python3 tools/tests/test_xref_claims.py [<asm>] (defaults to ASM env / standard install discovery)
"""

import os
import re
import subprocess
import sys
import tempfile

import _common

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(TOOLS)
DOCS = os.path.join(REPO, "docs")
XREF = os.path.join(TOOLS, "bin", "Xref.exe")

CLAIM = re.compile(r"`?([A-Za-z_]\w*)(?:\.|::)([A-Za-z_]\w*)`?\s*[^(`\n]*?\(Xref=(\d+)")


def claims_in(path: str) -> list[tuple[str, str, int]]:
    out = []
    with open(path, encoding="utf-8") as f:
        text = f.read()
    for m in CLAIM.finditer(text):
        out.append((m.group(1), m.group(2), int(m.group(3))))
    return out


def xref_counts(asm: str, pairs: list[tuple[str, str]]) -> dict[tuple[str, str], int]:
    """One Xref.exe invocation for every claim.

    --batch reads '<Type><TAB><Member>' lines and prints '<Type>::<Member> = N'
    totals from a single assembly pass; per-claim subprocesses would each pay a
    full mono + Cecil load (the test was ~6x slower that way).
    """
    with tempfile.TemporaryDirectory(prefix="xref-batch-", dir=_common.scratch_dir()) as td:
        claims_path = os.path.join(td, "claims.tsv")
        with open(claims_path, "w", encoding="utf-8") as f:
            for typ, member in pairs:
                f.write(f"{typ}\t{member}\n")
        r = subprocess.run(
            ["mono", XREF, asm, "--batch", claims_path], capture_output=True, text=True
        )
    if r.returncode != 0:
        return {}
    out: dict[tuple[str, str], int] = {}
    for line in r.stdout.splitlines():
        m = re.match(r"(.+)::(.+) = (\d+)$", line)
        if m:
            out[(m.group(1), m.group(2))] = int(m.group(3))
    return out


def main() -> int:
    asm_path, asm_label = _common.resolve_asm(sys.argv[1] if len(sys.argv) > 1 else None)
    if asm_path is None:
        print(f"SKIP: assembly not found: {asm_label}")
        return 0
    asm = str(asm_path)
    if not os.path.exists(XREF):
        print("SKIP: Xref.exe not built (run make tools)")
        return 0

    found = []
    for name in sorted(os.listdir(DOCS)):
        path = os.path.join(DOCS, name)
        if not name.endswith(".md") or os.path.isdir(path):
            continue
        for typ, member, want in claims_in(path):
            found.append((name, typ, member, want))

    # One assembly pass for all unique claims.
    pairs: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for _, typ, member, _ in found:
        if (typ, member) not in seen:
            seen.add((typ, member))
            pairs.append((typ, member))
    counts = xref_counts(asm, pairs)

    bad = []
    total = 0
    for name, typ, member, want in found:
        total += 1
        key = (typ, member)
        if key not in counts:
            bad.append(f"{name}: {typ}::{member} - Xref tool error")
        elif counts[key] != want:
            bad.append(f"{name}: `{typ}::{member}` doc Xref={want} but DLL Xref={counts[key]}")
    if bad:
        for b in bad:
            print("FAIL: " + b)
        print(f"FAIL: {len(bad)} of {total} Xref claims wrong")
        return 1
    print(f"OK: {total} Xref=N claims verified against the DLL")
    return 0


if __name__ == "__main__":
    sys.exit(main())
