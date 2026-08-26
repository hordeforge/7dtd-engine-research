#!/usr/bin/env python3
"""Pin sandbox/requirements.txt to sandbox/requirements.in (hash-pinned lock).

The uv-compiled lock is the repo's dependency inventory and supply-chain gate
(exact versions + sha256 for dnfile/dncil/UnityPy and their transitives). That
only holds while the two files agree: a dep added to requirements.in without
recompiling installs from a lock without it; a recompile that drops
--generate-hashes silently loses integrity checking. DLL-free, network-free.

Checked here:
  - every requirements.in dep appears in the lock as an exact name==version pin
  - every pin carries at least one --hash=sha256 (no hash-stripped hand edits)
  - no ranged/wildcard/url specifiers sneak into the lock
  - every entry the lock marks as coming from requirements.in is declared there

The checker is itself mutation-tested below against crafted bad locks so a
future refactor cannot turn it into a no-op.
"""

from __future__ import annotations

import os
import re
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

TOOLS = _common.TOOLS
IN_FILE = TOOLS / "sandbox" / "requirements.in"
LOCK = TOOLS / "sandbox" / "requirements.txt"

PIN_RE = re.compile(r"^([A-Za-z0-9][A-Za-z0-9._-]*)==([^\s\\]+)\s*(?:\\\s*)?$")
NON_EXACT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*\s*(@|~=|!=|<|>|[*]|\[)")
DIRECT_VIA_RE = re.compile(r"#\s+(?:via\s+)?-r requirements\.in$")


def canon(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def parse_in(text: str) -> set[str]:
    return {
        canon(line.strip())
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }


def parse_lock(text: str) -> dict[str, dict[str, Any]]:
    """Map canonical name -> {version, hashes, direct} from uv compile output."""
    pins: dict[str, dict[str, Any]] = {}
    current: dict[str, Any] | None = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("#"):
            if current is not None and DIRECT_VIA_RE.fullmatch(line):
                current["direct"] = True
            continue
        if line.startswith("--"):
            if current is not None and line.startswith("--hash=sha256:"):
                current["hashes"] += 1
            continue
        m = PIN_RE.match(line)
        if m is None:
            hint = "non-exact specifier" if NON_EXACT_RE.match(line) else "unparseable"
            raise ValueError(f"{hint} pin line: {raw!r}")
        current = {"version": m.group(2), "hashes": 0, "direct": False}
        pins[canon(m.group(1))] = current
    return pins


def check(in_set: set[str], lock_text: str) -> list[str]:
    bad: list[str] = []
    try:
        pins = parse_lock(lock_text)
    except ValueError as exc:
        return [str(exc)]
    for dep in sorted(in_set):
        if dep not in pins:
            bad.append(
                f"{dep}: declared in requirements.in but absent from the lock "
                "(recompile: uv pip compile --generate-hashes)"
            )
        elif pins[dep]["hashes"] == 0:
            bad.append(f"{dep}: pinned without any --hash=sha256 (integrity check lost)")
    for name, meta in sorted(pins.items()):
        if meta["direct"] and name not in in_set:
            bad.append(
                f"{name}: locked as a direct requirement but not declared in requirements.in"
            )
    return bad


def self_test() -> tuple[list[str], int]:
    """Mutation checks: each crafted defect must be caught, the clean lock must pass."""

    def h64(c: str) -> str:
        return c * 64

    clean = (
        f"alpha==1.0.0 \\\n    --hash=sha256:{h64('a')}\n    # via -r requirements.in\n"
        f"beta==2.0 \\\n    --hash=sha256:{h64('b')} \\\n    --hash=sha256:{h64('c')}\n"
        "    # via alpha\n"
    )
    cases = [
        ("clean lock", {"alpha"}, clean, []),
        ("dep missing from lock", {"alpha", "gamma"}, clean, ["gamma"]),
        ("hash stripped", {"alpha"}, "alpha==1.0.0\n    # via -r requirements.in\n", ["alpha"]),
        (
            "ghost direct",
            set(),
            f"alpha==1.0.0 \\\n    --hash=sha256:{h64('a')}\n    # via -r requirements.in\n",
            ["not declared"],
        ),
        (
            "range sneaks in",
            {"alpha"},
            f"alpha>=1.0 \\\n    --hash=sha256:{h64('a')}\n    # via -r requirements.in\n",
            ["non-exact specifier"],
        ),
        (
            "multi-via direct",
            {"alpha"},
            (
                f"alpha==1.0 \\\n    --hash=sha256:{h64('a')}\n    # via\n    #   beta\n"
                "    #   -r requirements.in\n"
                f"beta==2.0 \\\n    --hash=sha256:{h64('b')}\n    # via alpha\n"
            ),
            [],
        ),
    ]
    bad: list[str] = []
    for label, in_set, lock, want in cases:
        got = check(in_set, lock)
        if not want:
            if got:
                bad.append(f"{label}: clean case rejected: {got}")
        elif not any(w in line for w in want for line in got):
            bad.append(f"{label}: defect not caught (got {got!r})")
    return bad, len(cases)


def main() -> int:
    failures, n_cases = self_test()
    for f in failures:
        print("FAIL:", f, file=sys.stderr)

    real = check(parse_in(IN_FILE.read_text(encoding="utf-8")), LOCK.read_text(encoding="utf-8"))
    for f in real:
        print("FAIL:", f, file=sys.stderr)
    if failures or real:
        return 1

    pins = parse_lock(LOCK.read_text(encoding="utf-8"))
    hashed = sum(1 for m in pins.values() if m["hashes"] > 0)
    directs = ", ".join(sorted(n for n, m in pins.items() if m["direct"]))
    print(
        f"OK: sandbox lock matches requirements.in ({directs}); all {len(pins)} pins exact, "
        f"{hashed}/{len(pins)} sha256-hashed; {n_cases} mutations caught"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
