#!/usr/bin/env python3
"""Assert the committed auto-generated inventories match a fresh regeneration.

WireBodies.exe -> netpackage-bodies.md and Coverage.exe -> coverage-report.md are
machine-generated. If the committed file differs from what the tool produces now,
the committed doc is stale (a wire edit in the game, or a tool change, was not
regenerated). A stale narrative is exactly the class of bug this catches.

Usage: python3 tools/tests/test_committed_inventories_current.py [asm]
"""
import os
import subprocess
import sys
import tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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

def check_generated(exe, args, committed_rel, label):
    committed = os.path.join(REPO, committed_rel)
    assert os.path.isfile(committed), f"missing committed file: {committed_rel}"
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as tf:
        tmp = tf.name
    rc, _, err = run(exe, *args, tmp)
    assert rc == 0, f"{exe} failed: {err}"
    fresh = open(tmp).read()
    current = open(committed).read()
    os.unlink(tmp)
    if fresh != current:
        # find the first differing line for the message
        a, b = current.splitlines(), fresh.splitlines()
        for i, (x, y) in enumerate(zip(a, b)):
            if x != y:
                print(f"  first diff at line {i+1}:\n    committed: {x[:100]}\n    fresh:     {y[:100]}")
                break
        raise AssertionError(
            f"{label} ({committed_rel}) is STALE: regenerate with the matching tool."
        )
    print(f"OK: {label} is current")

def main():
    asm = sys.argv[1] if len(sys.argv) > 1 else default_asm()
    docs = os.path.join(REPO, "docs")
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "bodies.md")
        rc, _, err = run("WireBodies.exe", asm, out)
        assert rc == 0, f"WireBodies.exe failed: {err}"
        fresh = open(out).read()
        committed = open(os.path.join(REPO, "docs/inventories/netpackage-bodies.md")).read()
        if fresh != committed:
            raise AssertionError("docs/inventories/netpackage-bodies.md is STALE: run tools/regen.sh")
        print("OK: netpackage-bodies.md is current")
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "report.md")
        rc, _, err = run("Coverage.exe", asm, docs, out)
        assert rc == 0, f"Coverage.exe failed: {err}"
        fresh = open(out).read()
        committed = open(os.path.join(REPO, "docs/inventories/coverage-report.md")).read()
        if fresh != committed:
            raise AssertionError("docs/inventories/coverage-report.md is STALE: run tools/regen.sh")
        print("OK: coverage-report.md is current")
    # StateMachines.exe is DLL-free: it scans the docs for mermaid diagrams, so
    # this check also runs in CI (test-docs gate).
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "state-machines.md")
        rc, _, err = run("StateMachines.exe", docs, out)
        assert rc == 0, f"StateMachines.exe failed: {err}"
        fresh = open(out).read()
        committed = open(os.path.join(REPO, "docs/inventories/state-machines.md")).read()
        if fresh != committed:
            raise AssertionError("docs/inventories/state-machines.md is STALE: run tools/regen.sh")
        print("OK: state-machines.md is current")
    print("ALL COMMITTED INVENTORIES ARE CURRENT")

if __name__ == "__main__":
    main()
