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
    "entityclass-props.md": (r"(\d+)\s+EntityClass prop-name constants", 187),
    "dedicated-leaves.md": (r"\((\d+)\)", 88),
    "state-machines.md": (r"all (\d+) modelled lifecycles", 74),
}


def check_package_framing_counts(bad: list[str]) -> None:
    """protocol-packages.md §6.23 self-claims '37 rows (18 conditional + 19
    always-present)'. The 18 live in a table; the 19 are a prose name list.
    If either half drifts the stated total must too."""
    text = open(os.path.join(REPO, "docs", "protocol-packages.md"), encoding="utf-8").read()
    m = re.search(r"all 37 rows\s*\((\d+) conditional \+ (\d+) always-present\)", text, re.S)
    if not m:
        bad.append(
            "protocol-packages.md: §6.23 no 'all 37 rows (N conditional + M always-present)' claim"
        )
        return
    want_cond, want_always = int(m.group(1)), int(m.group(2))
    seg = text[text.index("**Genuinely conditional") : text.index("## 7.")]
    cond_rows = len(re.findall(r"^\| `NetPackage[A-Za-z0-9]+` \| \d+ \|", seg, re.M))
    # always-present: backticked NetPackage names in the prose paragraph before
    # the first "#### " body subsection (the "## 7." boundary would sweep in
    # later-added ToClient body subsections such as NetPackageTurretSync)
    seg_start = text.index("**Always-present")
    seg_end = text.index("## 7.")
    sub = re.search(r"\n#### ", text[seg_start:seg_end])
    if sub:
        seg_end = seg_start + sub.start()
    para = text[seg_start:seg_end]
    always_names = set(re.findall(r"`(NetPackage[A-Za-z0-9]+)`", para))
    if cond_rows != want_cond:
        bad.append(
            f"protocol-packages.md: §6.23 conditional table has {cond_rows} rows, claim says {want_cond}"
        )
    if len(always_names) != want_always:
        bad.append(
            f"protocol-packages.md: §6.23 always-present list has {len(always_names)} names, claim says {want_always}"
        )


def main() -> int:
    idx = open(IDX, encoding="utf-8").read()
    bad: list[str] = []
    check_package_framing_counts(bad)
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
