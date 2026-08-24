#!/usr/bin/env python3
"""Assert the committed auto-generated inventories match a fresh regeneration.

WireBodies.exe -> netpackage-bodies.md and Coverage.exe -> coverage-report.md are
machine-generated. If the committed file differs from what the tool produces now,
the committed doc is stale (a wire edit in the game, or a tool change, was not
regenerated). A stale narrative is exactly the class of bug this catches.

Prerequisites: mono + tools/bin/{WireBodies,Coverage}.exe + the local dedicated
Assembly-CSharp.dll. With no local DLL the test SKIPs; with a DLL but unbuilt
bin it FAILs with the build command.

Usage: python3 tools/tests/test_committed_inventories_current.py [asm]
"""
from __future__ import annotations

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common


def check_generated(exe, args, committed_rel, label, out_path):
    committed = os.path.join(_common.REPO, committed_rel)
    assert os.path.isfile(committed), f"missing committed file: {committed_rel}"
    rc, _, err = _common.run_tool(exe, *args, out_path)
    assert rc == 0, f"{exe} failed: {err}"
    with open(out_path, encoding="utf-8") as f:
        fresh = f.read()
    with open(committed, encoding="utf-8") as f:
        current = f.read()
    if fresh != current:
        # find the first differing line for the message
        a, b = current.splitlines(), fresh.splitlines()
        for i, (x, y) in enumerate(zip(a, b, strict=False)):
            if x != y:
                print(f"  first diff at line {i+1}:\n    committed: {x[:100]}\n    fresh:     {y[:100]}")
                break
        raise AssertionError(
            f"{label} ({committed_rel}) is STALE: regenerate with the matching tool."
        )
    print(f"OK: {label} is current")


def main() -> int:
    msg, is_skip = _common.prereq(["WireBodies.exe", "Coverage.exe"])
    if msg:
        print(("SKIP: " if is_skip else "FAIL: ") + msg)
        return 0 if is_skip else 1

    asm_path, asm_label = _common.resolve_asm(
        sys.argv[1] if len(sys.argv) > 1 else None
    )
    if asm_path is None:
        print(f"SKIP: assembly not found: {asm_label}")
        return 0

    docs = os.path.join(_common.REPO, "docs")
    with tempfile.TemporaryDirectory(prefix="inventories-current-") as td:
        check_generated(
            "WireBodies.exe",
            [str(asm_path)],
            "docs/inventories/netpackage-bodies.md",
            "netpackage-bodies.md",
            os.path.join(td, "bodies.md"),
        )
        check_generated(
            "Coverage.exe",
            [str(asm_path), docs],
            "docs/inventories/coverage-report.md",
            "coverage-report.md",
            os.path.join(td, "report.md"),
        )
        # StateMachines.exe is DLL-free (it scans docs for mermaid diagrams);
        # test_state_machines_current.py is the CI-side gate for it.
        check_generated(
            "StateMachines.exe",
            [docs],
            "docs/inventories/state-machines.md",
            "state-machines.md",
            os.path.join(td, "state-machines.md"),
        )
    print("ALL COMMITTED INVENTORIES ARE CURRENT")
    return 0


if __name__ == "__main__":
    sys.exit(main())
