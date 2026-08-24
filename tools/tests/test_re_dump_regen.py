#!/usr/bin/env python3
"""Regression test: Cecil dumpers regenerate non-empty RE artifacts from local dedicated Assembly-CSharp.

Requires:
  - 7 Days to Die Dedicated Server install with Managed/Assembly-CSharp.dll
  - mcs + mono on PATH
  - Mono.Cecil.dll next to tools/

Does not redistribute game IL; writes only under a caller-supplied out dir or
tools/tests/_out (gitignored).
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

TOOLS = Path(__file__).resolve().parents[1]
DOCS = TOOLS.parent / "docs"
# Mono.Cecil is copied into bin/ by build.sh; legacy dumpers live in legacy/.
CECIL = TOOLS / "bin" / "Mono.Cecil.dll"
DUMPER = TOOLS / "legacy" / "DumpFrameEntries.cs"
EXE = TOOLS / "bin" / "legacy" / "DumpFrameEntries.exe"


def main() -> int:
    asm = _common.find_asm()
    if asm is None:
        print("SKIP: dedicated Assembly-CSharp.dll not found (set SEVENDTD_DS_DIR)")
        return 0
    if not CECIL.is_file():
        print("FAIL: missing Mono.Cecil.dll at", CECIL, file=sys.stderr)
        return 1
    if not DUMPER.is_file():
        print("FAIL: missing", DUMPER, file=sys.stderr)
        return 1

    out = Path(os.environ.get("RE_DUMP_OUT", TOOLS / "tests" / "_out" / "frame-entries"))
    out.mkdir(parents=True, exist_ok=True)

    EXE.parent.mkdir(parents=True, exist_ok=True)
    compile_cmd = ["mcs", f"-r:{CECIL}", f"-out:{EXE}", str(DUMPER)]
    print("RUN:", " ".join(compile_cmd))
    subprocess.check_call(compile_cmd, cwd=str(TOOLS))

    # Mono.Cecil.dll lives in bin/; make it resolvable at runtime.
    env = dict(os.environ, MONO_PATH=str(CECIL.parent))
    run_cmd = ["mono", str(EXE), str(asm), str(out)]
    print("RUN:", " ".join(run_cmd))
    subprocess.check_call(run_cmd, cwd=str(TOOLS), env=env)

    required = [
        out / "inventory-frame-entries.md",
        out / "inventory-gmupdate-calls.md",
        out / "inventory-manager-updates.md",
    ]
    for f in required:
        if not f.is_file() or f.stat().st_size < 50:
            print("FAIL: missing or tiny", f, file=sys.stderr)
            return 1
        text = f.read_text(encoding="utf-8", errors="replace")
        if f.name == "inventory-frame-entries.md":
            for needle in ("GameManager", "ConnectionManager", "DynamicMeshManager", "Update"):
                if needle not in text:
                    print("FAIL:", f, "missing", needle, file=sys.stderr)
                    return 1
        if f.name == "inventory-gmupdate-calls.md":
            for needle in ("UpdateTick", "gmUpdate", "ThreadManager"):
                if needle not in text:
                    print("FAIL:", f, "missing", needle, file=sys.stderr)
                    return 1

    # staleness guard: the committed docs must carry the regenerated bodies
    # (the committed wrappers - title, Kind/Prefer/Hub - may differ; the table
    # and leaf-list content from the first body row onward must match).
    committed = {
        out / "inventory-frame-entries.md": DOCS / "inventories" / "frame-entries.md",
        out / "inventory-gmupdate-calls.md": DOCS / "inventories" / "gmupdate-calls.md",
        out / "inventory-manager-updates.md": DOCS / "inventories" / "manager-updates.md",
    }
    for gen, doc in committed.items():
        if not doc.is_file():
            print("FAIL: missing committed", doc, file=sys.stderr)
            return 1
        gl = gen.read_text(encoding="utf-8", errors="replace").splitlines()
        dl = doc.read_text(encoding="utf-8", errors="replace").splitlines()
        body_pat = ("|", "- `", "1. IL_")
        gi = next((k for k, ln in enumerate(gl) if ln.strip().startswith(body_pat)), -1)
        di = next((k for k, ln in enumerate(dl) if ln.strip().startswith(body_pat)), -1)
        gbody = [ln for ln in gl[gi:] if ln.strip()]
        dbody = [ln for ln in dl[di:] if ln.strip()]
        if gi < 0 or di < 0 or gbody != dbody:
            print(
                "FAIL: committed doc stale vs regenerated dump:",
                doc.name,
                "(regenerate from the dumper output)",
                file=sys.stderr,
            )
            return 1

    print("OK: regenerated", out)
    for f in required:
        print(" ", f.name, f.stat().st_size, "bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
