#!/usr/bin/env python3
"""Guard the tools/README.md test table against the Makefile's actual test runs.

Every test script invoked by the `make test` / `make test-docs` / `make verify`
targets must be listed in the tools/README.md "Tests" table, every table entry
must be a real file, and every script in tools/tests/ must be invoked by a make
target (_common.py is the shared helper, not a gate). A gate that is written
but never wired in would otherwise sit green forever without ever running.

Usage: python3 tools/tests/test_readme_test_table.py
"""

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

TOOLS = _common.TOOLS
REPO = _common.REPO
MAKEFILE = os.path.join(REPO, "Makefile")
README = os.path.join(TOOLS, "README.md")
TESTDIR = os.path.join(TOOLS, "tests")
# Shared helper module, not a gate: it is imported by the gates, never run.
HELPERS = {"_common.py"}


def main() -> int:
    mk = Path(MAKEFILE).read_text(encoding="utf-8")
    run = set()
    for m in re.finditer(r"python3 \"\$\(TOOLS\)/tests/([A-Za-z0-9_.-]+\.py)\"", mk):
        run.add(m.group(1))
    readme = Path(README).read_text(encoding="utf-8")
    table = set(re.findall(r"tests/([A-Za-z0-9_.-]+\.py)", readme))
    bad = []
    # make help parity: every non-help target has a help line and vice versa
    targets = set(re.findall(r"^([a-z0-9-]+):", mk, re.M))
    helped = set(re.findall(r"@echo \"make ([a-z0-9-]+) ", mk))
    for t in sorted(targets - helped - {"help"}):
        bad.append(f"target `{t}` has no make help line")
    for t in sorted(helped - targets):
        bad.append(f"make help mentions `{t}` but no such target exists")
    for f in sorted(run - table):
        bad.append(f"{f}: run by make but missing from tools/README.md Tests table")
    for f in sorted(table - run):
        if not os.path.exists(os.path.join(TESTDIR, f)):
            bad.append(f"{f}: in README Tests table but file does not exist")
    # A gate wired into neither the Makefile nor the table was invisible to both
    # checks above: nothing ran it and nothing claimed it ran.
    present = {f for f in os.listdir(TESTDIR) if f.endswith(".py")} - HELPERS
    for f in sorted(present - run):
        bad.append(f"{f}: exists in tools/tests but no make target runs it")
    if bad:
        for b in bad:
            print("FAIL:", b)
        return 1
    print(f"OK: {len(run)} make-run test scripts all documented in tools/README.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
