#!/usr/bin/env python3
"""Assert no stale stock-transport claims linger in the narrative docs.

2026-08-10 closures that must not be re-broken by a future edit:
  - LiteNetLib.dll is a MANAGED .NET assembly, not a native plugin (the
    join-churn flake root cause is a managed race, docs/network.md 4.0).
  - Unity peer script order is observed, not unknown (docs/loop.md 1.1).
Any doc that still calls the transport "native LiteNetLib" / "LiteNet native"
or calls peer order "unknown" is stale relative to the residual table.

Usage: python3 tools/tests/test_transport_closure_claims.py
"""
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(REPO, "docs")

# (pattern, reason) - a match means the doc contradicts a closed claim.
STALE_PATTERNS = [
    (r"native\s+LiteNetLib", "LiteNetLib is managed (network.md 4.0)"),
    (r"LiteNetLib\s+native", "LiteNetLib is managed (network.md 4.0)"),
    (r"LiteNet\s+native", "LiteNetLib is managed (network.md 4.0)"),
    (r"native\s+LiteNet", "LiteNetLib is managed (network.md 4.0)"),
    (r"Unknown\s+peer\s+script\s+order", "peer order observed (loop.md 1.1)"),
]

def main():
    bad = []
    for root, _dirs, files in os.walk(DOCS):
        for name in files:
            if not name.endswith(".md"):
                continue
            path = os.path.join(root, name)
            text = open(path, encoding="utf-8").read()
            for pat, reason in STALE_PATTERNS:
                for m in re.finditer(pat, text, re.IGNORECASE):
                    line_no = text[: m.start()].count("\n") + 1
                    bad.append(f"{os.path.relpath(path, REPO)}:{line_no}: {m.group(0)!r} ({reason})")
    if bad:
        raise AssertionError(
            "Stale stock-transport claims found (see docs/network.md 4.0, docs/loop.md 1.1):\n"
            + "\n".join(bad)
        )
    print("OK: no stale native-LiteNetLib / unknown-peer-order claims in docs")

if __name__ == "__main__":
    main()
