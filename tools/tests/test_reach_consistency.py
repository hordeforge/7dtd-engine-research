#!/usr/bin/env python3
"""Assert the two reachability tools agree and the census buckets are sound.

Reach.exe and Coverage.exe share the seed definitions (tools/src/Seeds.cs) and the
same BFS (interface devirtualization + reflection-following). If one drifts, the
"reached methods" counts diverge - that is a hard failure here.

Also asserts the census arithmetic invariants:
  - narrated + catalogued + classified + unaccounted == game types (reached surface)
  - the whole-assembly partition sums exactly to all types.

Prerequisites: mono + tools/bin/{Coverage,Reach}.exe + the local dedicated
Assembly-CSharp.dll. With no local DLL the test SKIPs (nothing to assert);
with a DLL but unbuilt bin it FAILs with the build command.

Usage: python3 tools/tests/test_reach_consistency.py [asm]
"""

from __future__ import annotations

import os
import re
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common


def main() -> int:
    msg, is_skip = _common.prereq(["Coverage.exe", "Reach.exe"])
    if msg:
        print(("SKIP: " if is_skip else "FAIL: ") + msg)
        return 0 if is_skip else 1

    asm_path, asm_label = _common.resolve_asm(sys.argv[1] if len(sys.argv) > 1 else None)
    if asm_path is None:
        print(f"SKIP: assembly not found: {asm_label}")
        return 0

    docs = os.path.join(_common.REPO, "docs")
    with tempfile.TemporaryDirectory(prefix="reach-consistency-") as td:
        report = os.path.join(td, "coverage-report.md")
        tsv = os.path.join(td, "reach.tsv")

        rc, _, cov_err = _common.run_tool("Coverage.exe", str(asm_path), docs, report)
        assert rc == 0, f"Coverage.exe failed: {cov_err}"
        m = re.search(r"reached methods=(\d+)", cov_err)
        assert m, f"could not parse Coverage reached methods: {cov_err}"
        cov_methods = int(m.group(1))

        rc, _, reach_err = _common.run_tool("Reach.exe", str(asm_path), tsv)
        assert rc == 0, f"Reach.exe failed: {reach_err}"
        m = re.search(r"reached methods=(\d+)", reach_err)
        assert m, f"could not parse Reach reached methods: {reach_err}"
        reach_methods = int(m.group(1))

        with open(report, encoding="utf-8") as f:
            text = f.read()

    assert cov_methods == reach_methods, (
        f"SEED/BFS DRIFT: Coverage reached methods={cov_methods} != Reach {reach_methods}. "
        "tools/src/Seeds.cs or the BFS in one tool changed without the other."
    )
    print(f"OK: Coverage and Reach agree on reached methods ({cov_methods})")

    # Bucket invariant from the report.
    def row(key):
        m = re.search(
            r"\| \.\.\.\*\*"
            + re.escape(key)
            + r"\*\*[^|]*\| \*{0,2}(\d+)(?: \([^)]*\))?\*{0,2} \|",
            text,
        )
        return int(m.group(1)) if m else None

    game = row("game types")
    narrated = row("narrated")
    catalogued = row("catalogued only")
    classified = row("classified")
    unaccounted = row("unaccounted")
    assert None not in (game, narrated, catalogued, classified, unaccounted), (
        "missing bucket row in report"
    )
    assert narrated + catalogued + classified + unaccounted == game, (
        f"bucket invariant broken: {narrated}+{catalogued}+{classified}+{unaccounted} != {game}"
    )
    print(f"OK: reached-surface buckets sum to game types ({game})")

    # Whole-assembly partition: accounted + excluded == all types.
    m = re.search(
        r"Accounted game types \(reached documented \+ unreached classified\) \| \*\*(\d+) / (\d+) \(100%\)\*\*",
        text,
    )
    assert m, "missing whole-assembly accounted row"
    accounted, total = int(m.group(1)), int(m.group(2))
    assert accounted == total, f"whole-assembly accounting not 100%: {accounted}/{total}"
    m = re.search(
        r"excluded by design: (\d+) compiler-generated, (\d+) third-party/BCL, (\d+) both; sums to (\d+) of (\d+)",
        text,
    )
    assert m, "missing excluded-by-design partition row"
    gen, lib, both, partition, all_types = (int(m.group(i)) for i in range(1, 6))
    assert accounted + gen + lib + both == all_types == partition, (
        f"partition broken: {accounted}+{gen}+{lib}+{both} != {all_types}"
    )
    print(f"OK: whole-assembly partition sums to all types ({all_types})")
    print("ALL CONSISTENCY CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
