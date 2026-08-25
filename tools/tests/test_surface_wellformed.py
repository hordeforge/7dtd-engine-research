#!/usr/bin/env python3
"""Assert the FullSurface output is well-formed and internally consistent.

FullSurface emits per-type and per-namespace markdown tables. Compiler-generated
state-machine type names can embed a pipe (e.g. `...Privileges|1>d`), which used
to break the table rows: 23 rows were malformed and the naive per-type IL sum
read 1,738,381 instead of the true 1,740,737 (full-surface.md). Since the
2026-08-11 escape fix the two tables must agree and the total must match the
documented pin.

Usage: python3 tools/tests/test_surface_wellformed.py [<asm>] (defaults to ASM env / standard install discovery)
"""

import os
import re
import subprocess
import sys
import tempfile

import _common

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPECTED_IL_TOTAL = 1740737  # docs/full-surface.md: "1,740,737 IL instructions"

PIPE_AWARE = re.compile(r"(?<!\\)\|")  # split on | not preceded by backslash


def split_cells(line: str) -> list[str]:
    return [c.strip() for c in PIPE_AWARE.split(line.strip())]


def parse_types_table(text: str):
    rows = 0
    total = 0
    malformed = []
    for line in text.splitlines():
        if not line.startswith("|") or line.startswith("|---"):
            continue
        cells = split_cells(line)
        if cells[1] == "Type":
            continue
        rows += 1
        if len(cells) != 9:
            malformed.append(line[:80])
            continue
        total += int(cells[7])
    return rows, total, malformed


def main() -> int:
    asm_path, asm_label = _common.resolve_asm(sys.argv[1] if len(sys.argv) > 1 else None)
    if asm_path is None:
        print(f"SKIP: assembly not found: {asm_label}")
        return 0
    asm = str(asm_path)
    env = dict(os.environ)
    env["MONO_PATH"] = os.path.join(TOOLS, "bin")
    with tempfile.TemporaryDirectory() as tmp:
        proc = subprocess.run(
            ["mono", os.path.join(TOOLS, "bin", "FullSurface.exe"), asm, tmp],
            capture_output=True,
            text=True,
            env=env,
        )
        assert proc.returncode == 0, f"FullSurface failed: {proc.stderr}"
        types = open(os.path.join(tmp, "surface-types.md"), encoding="utf-8").read()
        namespaces = open(os.path.join(tmp, "surface-namespaces.md"), encoding="utf-8").read()

    rows, type_total, malformed = parse_types_table(types)
    assert not malformed, f"{len(malformed)} malformed surface-types rows:\n" + "\n".join(
        malformed[:5]
    )

    ns_total = 0
    for line in namespaces.splitlines():
        if line.startswith("| Namespace") or line.startswith("|---"):
            continue
        cells = split_cells(line)
        if len(cells) == 7:  # '', ns, types, methods, IL, fields, ''
            ns_total += int(cells[4])
    assert type_total == ns_total, (
        f"per-type IL sum {type_total} != per-namespace IL sum {ns_total} (pipe-escape regression?)"
    )
    assert type_total == EXPECTED_IL_TOTAL, (
        f"IL total {type_total} != documented {EXPECTED_IL_TOTAL} (full-surface.md)"
    )
    print(
        f"OK: surface well-formed; {rows} type rows, IL total {type_total} matches full-surface.md"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
