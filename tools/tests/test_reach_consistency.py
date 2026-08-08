#!/usr/bin/env python3
"""Assert the two reachability tools agree and the census buckets are sound.

Reach.exe and Coverage.exe share the seed definitions (tools/src/Seeds.cs) and the
same BFS (interface devirtualization + reflection-following). If one drifts, the
"reached methods" counts diverge - that is a hard failure here.

Also asserts the census arithmetic invariants:
  - narrated + catalogued + classified + unaccounted == game types (reached surface)
  - the whole-assembly partition sums exactly to all types.

Usage: python3 tools/tests/test_reach_consistency.py [asm]
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
REPO = os.path.dirname(TOOLS)

def default_asm():
    env = os.environ.get("ASM")
    if env:
        return env
    home = os.path.expanduser("~")
    return os.path.join(
        home,
        ".local/share/Steam/steamapps/common/7 Days to Die Dedicated Server/"
        "7DaysToDieServer_Data/Managed/Assembly-CSharp.dll",
    )

def run(exe, *args):
    env = dict(os.environ)
    env["MONO_PATH"] = os.path.join(TOOLS, "bin")
    proc = subprocess.run(
        ["mono", os.path.join(TOOLS, "bin", exe), *args],
        capture_output=True, text=True, env=env,
    )
    return proc.returncode, proc.stdout, proc.stderr

def main():
    asm = sys.argv[1] if len(sys.argv) > 1 else default_asm()
    docs = os.path.join(REPO, "docs")
    report = "/tmp/test-reach-consistency-report.md"

    rc, _, cov_err = run("Coverage.exe", asm, docs, report)
    assert rc == 0, f"Coverage.exe failed: {cov_err}"
    m = re.search(r"reached methods=(\d+)", cov_err)
    assert m, f"could not parse Coverage reached methods: {cov_err}"
    cov_methods = int(m.group(1))

    rc, _, reach_err = run("Reach.exe", asm, "/tmp/test-reach-consistency.tsv")
    assert rc == 0, f"Reach.exe failed: {reach_err}"
    m = re.search(r"reached methods=(\d+)", reach_err)
    assert m, f"could not parse Reach reached methods: {reach_err}"
    reach_methods = int(m.group(1))

    assert cov_methods == reach_methods, (
        f"SEED/BFS DRIFT: Coverage reached methods={cov_methods} != Reach {reach_methods}. "
        "tools/src/Seeds.cs or the BFS in one tool changed without the other."
    )
    print(f"OK: Coverage and Reach agree on reached methods ({cov_methods})")

    # Bucket invariant from the report.
    text = open(report).read()
    def row(key):
        m = re.search(r"\| \.\.\.\*\*" + re.escape(key) + r"\*\*[^|]*\| \*{0,2}(\d+)(?: \([^)]*\))?\*{0,2} \|", text)
        return int(m.group(1)) if m else None
    game = row("game types")
    narrated = row("narrated")
    catalogued = row("catalogued only")
    classified = row("classified")
    unaccounted = row("unaccounted")
    assert None not in (game, narrated, catalogued, classified, unaccounted), "missing bucket row in report"
    assert narrated + catalogued + classified + unaccounted == game, (
        f"bucket invariant broken: {narrated}+{catalogued}+{classified}+{unaccounted} != {game}"
    )
    print(f"OK: reached-surface buckets sum to game types ({game})")

    # Whole-assembly partition: accounted + excluded == all types.
    m = re.search(r"Accounted game types \(reached documented \+ unreached classified\) \| \*\*(\d+) / (\d+) \(100%\)\*\*", text)
    assert m, "missing whole-assembly accounted row"
    accounted, total = int(m.group(1)), int(m.group(2))
    assert accounted == total, f"whole-assembly accounting not 100%: {accounted}/{total}"
    m = re.search(r"excluded by design: (\d+) compiler-generated, (\d+) third-party/BCL, (\d+) both; sums to (\d+) of (\d+)", text)
    assert m, "missing excluded-by-design partition row"
    gen, lib, both, partition, all_types = (int(m.group(i)) for i in range(1, 6))
    assert accounted + gen + lib + both == all_types == partition, (
        f"partition broken: {accounted}+{gen}+{lib}+{both} != {all_types}"
    )
    print(f"OK: whole-assembly partition sums to all types ({all_types})")
    print("ALL CONSISTENCY CHECKS PASSED")

if __name__ == "__main__":
    main()
