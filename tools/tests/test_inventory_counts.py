#!/usr/bin/env python3
"""Guard the INDEX inventory-count claims against the inventories' own stated counts.

docs/INDEX.md states a count per inventory (e.g. "123 SequenceAction leaves").
Each inventory's header self-states its count, derived from the IL (the table
may carry more rows than the leaf count when base/intermediate types are
included). If either side drifts without the other, the corpus is
inconsistent - this test requires the INDEX claim number to appear in the
inventory's own text.

Usage: python3 tools/tests/test_inventory_counts.py
"""
import os
import re
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(TOOLS)
INV = os.path.join(REPO, "docs", "inventories")
IDX = os.path.join(REPO, "docs", "INDEX.md")

# inventory -> (INDEX claim pattern, expected number)
CLAIMS = {
    "sequence-actions.md": (r"(\d+)\s+SequenceAction leaves", 123),
    "block-behaviors.md": (r"(\d+)\s+Block leaves", 65),
    "item-actions.md": (r"(\d+)\s+ItemAction leaves", 38),
    "minevent-actions.md": (r"(\d+)\s+triggered-effect leaves", 71),
    "te-features.md": (r"(\d+)\s+TEFeatureAbs leaves", 11),
    "challenge-objectives.md": (r"(\d+)\s+objective leaves", 28),
    "quest-objectives.md": (r"(\d+)\s+objectives", 38),
    "console-command-list.md": (r"(\d+)\s+commands", 188),
    "xmlsToLoad.md": (r"(\d+)\s+WorldStaticData XmlLoadInfo rows", 49),
    "dedicated-leaves.md": (r"\((\d+)\)", 88),
    "state-machines.md": (r"all (\d+) modelled lifecycles", 74),
}


def main() -> int:
    idx = open(IDX, encoding="utf-8").read()
    bad = []
    for name, (pat, expected) in CLAIMS.items():
        text = open(os.path.join(INV, name), encoding="utf-8", errors="replace").read()
        m = re.search(pat, idx)
        if not m:
            bad.append(f"{name}: no INDEX claim matching /{pat}/")
            continue
        claimed = int(m.group(1))
        if claimed != expected:
            bad.append(f"{name}: INDEX claim {claimed} != expected {expected}")
            continue
        # the claimed number must be corroborated in the inventory's own text
        if not re.search(rf"\b{expected}\b", text):
            bad.append(f"{name}: inventory does not self-state {expected}")
    if bad:
        for b in bad:
            print("FAIL:", b)
        return 1
    print(f"OK: {len(CLAIMS)} inventory count claims agree with the inventories")
    return 0


if __name__ == "__main__":
    sys.exit(main())
