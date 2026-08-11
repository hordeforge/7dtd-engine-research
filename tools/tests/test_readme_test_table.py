#!/usr/bin/env python3
"""Guard the tools/README.md test table against the Makefile's actual test runs.

Every test script invoked by the `make test` / `make test-docs` / `make verify`
targets must be listed in the tools/README.md "Tests" table, and every table
entry must be a real file. Adding a gate without documenting it (or removing a
script without cleaning the table) fails here.

Usage: python3 tools/tests/test_readme_test_table.py
"""
import os
import re
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(TOOLS)
MAKEFILE = os.path.join(REPO, "Makefile")
README = os.path.join(TOOLS, "README.md")
TESTDIR = os.path.join(TOOLS, "tests")

# scripts that are run directly (not via python3 <path>), e.g. stock-sync.sh
SKIP = {"stock-sync.sh"}


def main() -> int:
    mk = open(MAKEFILE, encoding="utf-8").read()
    run = set()
    for m in re.finditer(r"python3 \"\$\(TOOLS\)/tests/([A-Za-z0-9_.-]+\.py)\"", mk):
        run.add(m.group(1))
    # also the bench/check scripts invoked by the targets above
    for m in re.finditer(r"python3 \"\$\(TOOLS\)/tests/([A-Za-z0-9_.-]+\.py)\"", mk):
        run.add(m.group(1))
    readme = open(README, encoding="utf-8").read()
    table = set(re.findall(r"tests/([A-Za-z0-9_.-]+\.py)", readme))
    bad = []
    for f in sorted(run - table):
        bad.append(f"{f}: run by make but missing from tools/README.md Tests table")
    for f in sorted(table - run):
        if not os.path.exists(os.path.join(TESTDIR, f)):
            bad.append(f"{f}: in README Tests table but file does not exist")
    if bad:
        for b in bad:
            print("FAIL:", b)
        return 1
    print(f"OK: {len(run)} make-run test scripts all documented in tools/README.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
