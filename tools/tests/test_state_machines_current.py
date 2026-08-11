#!/usr/bin/env python3
"""State-machines inventory staleness (DLL-free, runs in CI).

StateMachines.exe scans the docs for mermaid state diagrams and regenerates
docs/inventories/state-machines.md. A doc edit that adds/removes a diagram
without regenerating the inventory fails here.

Usage: python3 tools/tests/test_state_machines_current.py
"""
import os
import subprocess
import sys
import tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(TOOLS)
COMMITTED = os.path.join(REPO, "docs", "inventories", "state-machines.md")


def main() -> int:
    env = dict(os.environ)
    env["MONO_PATH"] = os.path.join(TOOLS, "bin")
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "state-machines.md")
        proc = subprocess.run(
            ["mono", os.path.join(TOOLS, "bin", "StateMachines.exe"), os.path.join(REPO, "docs"), out],
            capture_output=True, text=True, env=env,
        )
        if proc.returncode != 0:
            print(f"FAIL: StateMachines.exe: {proc.stderr}")
            return 1
        fresh = open(out, encoding="utf-8").read()
        committed = open(COMMITTED, encoding="utf-8").read()
    if fresh != committed:
        print("FAIL: docs/inventories/state-machines.md is STALE (regenerate with StateMachines.exe)")
        return 1
    print("OK: state-machines.md is current")
    return 0


if __name__ == "__main__":
    sys.exit(main())
