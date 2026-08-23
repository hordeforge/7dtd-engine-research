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

# One stale sentence per pattern, same order. The self-test proves each regex
# can actually fire; without it a typo'd pattern would make this gate pass
# forever while stale claims crept back in.
STALE_SAMPLES = [
    "the join uses the native LiteNetLib plugin directly",
    "LiteNetLib native transport layer",
    "packets cross the LiteNet native stack",
    "a native LiteNet wrapper module",
    "Unknown peer script order was assumed",
]

# Must never match any pattern, or every clean doc would fail the gate.
CLEAN_SAMPLE = (
    "# network\n"
    "LiteNetLib is a managed .NET assembly.\n"
    "Unity peer script order was observed directly.\n"
    "The join-churn flake root cause is a managed race.\n"
)


def self_test_patterns() -> None:
    if len(STALE_SAMPLES) != len(STALE_PATTERNS):
        raise AssertionError(
            f"self-test misconfigured: {len(STALE_SAMPLES)} samples for "
            f"{len(STALE_PATTERNS)} patterns"
        )
    problems = []
    for (pat, _reason), sample in zip(STALE_PATTERNS, STALE_SAMPLES):
        # Same flags as the doc scan below: the self-test must prove the
        # deployed detector fires, not a stricter case-sensitive variant.
        if not re.search(pat, sample, re.IGNORECASE):
            problems.append(f"pattern cannot fire: {pat!r}")
    for pat, _reason in STALE_PATTERNS:
        m = re.search(pat, CLEAN_SAMPLE, re.IGNORECASE)
        if m:
            problems.append(f"pattern flags clean text: {pat!r} matched {m.group(0)!r}")
    if problems:
        raise AssertionError(
            "stale-claim detector self-test failed:\n  " + "\n  ".join(problems)
        )


def main():
    self_test_patterns()
    bad = []
    for root, _dirs, files in os.walk(DOCS):
        for name in files:
            if not name.endswith(".md"):
                continue
            path = os.path.join(root, name)
            with open(path, encoding="utf-8") as f:
                text = f.read()
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
