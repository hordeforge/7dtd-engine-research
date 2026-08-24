#!/usr/bin/env python3
"""Guard the hand-corrections that tools/data/promoted-types.txt pins.

docs/out-of-scope-surface.md was machine-generated, then hand-corrected: 48+
types whose referrers are server-dominant were promoted out of it (list in
tools/data/promoted-types.txt). A naive regeneration of the name-based
classifier would silently pull them back in. This gate makes the promotion
list an enforced tool input: every listed name must still be absent from the
out-of-scope classification, and the file must stay parseable and unique.

DLL-free; runs in CI.

Usage: python3 tools/tests/test_promoted_types.py
"""

from __future__ import annotations

import os
import re
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(TOOLS)
PROMOTED = os.path.join(TOOLS, "data", "promoted-types.txt")
OOS = os.path.join(REPO, "docs", "out-of-scope-surface.md")

IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def load_promoted() -> list[str]:
    names: list[str] = []
    with open(PROMOTED, encoding="utf-8") as fh:
        for ln, line in enumerate(fh, 1):
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            assert IDENT.match(s), f"{PROMOTED}:{ln}: not an identifier: {s!r}"
            names.append(s)
    return names


def main() -> int:
    names = load_promoted()
    assert names, f"{PROMOTED}: no entries; the guard would be vacuous"
    dupes = sorted({n for n in names if names.count(n) > 1})
    assert not dupes, f"{PROMOTED}: duplicate entries: {dupes}"

    with open(OOS, encoding="utf-8") as fh:
        oos_rows = set(re.findall(r"^\| `([A-Za-z_][A-Za-z0-9_]*)`", fh.read(), re.M))

    # The doc also carries aggregate counts in its header tables; those cells
    # are bare numbers, so a row match is the only way a type can re-enter.
    back = sorted(set(names) & oos_rows)
    assert not back, (
        f"promoted types re-classified out-of-scope in {os.path.relpath(OOS, REPO)} "
        f"(a regeneration reverted the hand-correction): {back}"
    )

    # The maintenance note must keep pointing regenerators at the input file.
    with open(OOS, encoding="utf-8") as fh:
        note = fh.read(4000)
    assert "promoted-types.txt" in note, (
        "out-of-scope-surface.md header no longer references "
        "tools/data/promoted-types.txt; regenerators will not know the input"
    )
    print(
        f"OK: {len(names)} promoted types absent from out-of-scope-surface.md; "
        "maintenance note intact"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
