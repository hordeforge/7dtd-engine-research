#!/usr/bin/env python3
"""Assert the committed auto-generated inventories match a fresh regeneration.

WireBodies.exe -> netpackage-bodies.md and Coverage.exe -> coverage-report.md are
machine-generated. If the committed file differs from what the tool produces now,
the committed doc is stale (a wire edit in the game, or a tool change, was not
regenerated). A stale narrative is exactly the class of bug this catches.

The comparison only runs when the local assembly IS the studied build: a live
DLL whose version differs from stock_facts.json means regeneration would retarget
generated docs away from the pin, so the test SKIPs with both versions named.

Prerequisites: mono + tools/bin/{StockFacts,WireBodies,Coverage}.exe + the local
dedicated Assembly-CSharp.dll matching the pin. With no local DLL the test SKIPs;
with a DLL but unbuilt bin it FAILs with the build command.

Usage: python3 tools/tests/test_committed_inventories_current.py [asm]
"""

from __future__ import annotations

import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

FACTS = os.path.join(_common.TOOLS, "data", "stock_facts.json")


def live_build_matches_pin(asm_path) -> tuple[bool, str]:
    """True when the local assembly is the build the corpus pins.

    The generated inventories are pinned to the studied build (stock_facts.json
    version). A Steam update or downgrade leaves the committed docs CORRECT and
    a fresh regeneration WRONG, so a version mismatch must skip the staleness
    comparison instead of reporting the inventory stale.
    """
    with tempfile.TemporaryDirectory(prefix="inventories-version-") as td:
        out = os.path.join(td, "live_facts.json")
        rc, _, err = _common.run_tool("StockFacts.exe", str(asm_path), out)
        if rc != 0:
            return True, f"StockFacts.exe failed ({err.strip()[:120]}); cannot version-check"
        try:
            with open(out, encoding="utf-8") as f:
                live = json.load(f)["version"]
            with open(FACTS, encoding="utf-8") as f:
                pin = json.load(f)["version"]
        except (json.JSONDecodeError, KeyError, OSError) as exc:
            return True, f"facts unreadable ({exc}); cannot version-check"
        triple = ("major", "minor", "build")
        if all(live.get(k) == pin.get(k) for k in triple):
            return True, ""
        return False, (
            f"SKIP: live DLL is {live.get('display')} (b{live.get('build')}) but the "
            f"corpus pins {pin.get('display')} (b{pin.get('build')}); committed "
            f"inventories stay pinned to the studied build. Point ASM at that build "
            f"or re-pin: ASM=<dll> tools/post-update.sh"
        )


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
                print(
                    f"  first diff at line {i + 1}:\n    committed: {x[:100]}\n    fresh:     {y[:100]}"
                )
                break
        raise AssertionError(
            f"{label} ({committed_rel}) is STALE: regenerate with the matching tool."
        )
    print(f"OK: {label} is current")


def main() -> int:
    msg, is_skip = _common.prereq(["StockFacts.exe", "WireBodies.exe", "Coverage.exe"])
    if msg:
        print(("SKIP: " if is_skip else "FAIL: ") + msg)
        return 0 if is_skip else 1

    asm_path, asm_label = _common.resolve_asm(sys.argv[1] if len(sys.argv) > 1 else None)
    if asm_path is None:
        print(f"SKIP: assembly not found: {asm_label}")
        return 0

    same_build, note = live_build_matches_pin(asm_path)
    if not same_build:
        print(note)
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
