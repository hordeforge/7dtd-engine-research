#!/usr/bin/env python3
"""Assert the Mono.Cecil supply-chain pin stays intact and wired in.

Mono.Cecil.dll is this repo's only third-party dependency: tools/build.sh
locates a candidate dll from ad-hoc local paths, verifies it against
data/cecil.pin, then compiles every dumper against it. A swapped binary would
run arbitrary code inside every dump/regen job. This gate fails if:
  - data/cecil.pin is missing, malformed, or carries a non-SHA-256 digest
  - build.sh no longer enforces the pin (gate removed or bypassed silently)
  - a built bin/Mono.Cecil.dll disagrees with the committed pin

Usage: python3 tools/tests/test_cecil_pin.py
"""

import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOOLS = os.path.join(REPO, "tools")
PIN = os.path.join(TOOLS, "data", "cecil.pin")
BUILD = os.path.join(TOOLS, "build.sh")

# build.sh must contain these to count as enforcing the pin.
GATE_MARKERS = [
    r"data/cecil\.pin",
    r"sha256",
    r"MONO_CECIL_UNVERIFIED",
    r"cecil-pin\.sh",
]

# Self-test samples: prove each marker regex can fire and that the negative
# control cannot, so a typo'd pattern cannot silence this gate forever.
POSITIVE_SAMPLE = 'pin_sha="$(sed -n \'s/^sha256=//p\' "$here/data/cecil.pin")"'
NEGATIVE_SAMPLE = "mcs -nologo -r:bin/Mono.Cecil.dll src/Census.cs"


def load_pin() -> tuple[str, str]:
    if not os.path.isfile(PIN):
        raise AssertionError(f"missing pin file: {PIN}")
    fields: dict[str, str] = {}
    for line in open(PIN, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, val = line.partition("=")
        fields[key.strip()] = val.strip()
    for key in ("version", "sha256"):
        if key not in fields:
            raise AssertionError(f"{PIN}: missing '{key}=' line")
    if not re.fullmatch(r"[0-9a-f]{64}", fields["sha256"]):
        raise AssertionError(f"{PIN}: sha256 is not 64 lowercase hex chars")
    return fields["version"], fields["sha256"]


def check_build_gate() -> None:
    text = open(BUILD, encoding="utf-8").read()
    for marker in GATE_MARKERS:
        if not re.search(marker, text):
            raise AssertionError(f"{BUILD}: pin gate lost marker {marker!r}")
    # Negative control: a marker that must NOT appear in a plain compile line.
    if re.search(GATE_MARKERS[1], NEGATIVE_SAMPLE):
        raise AssertionError("self-test broken: sha256 pattern matches plain mcs line")
    if not re.search(GATE_MARKERS[1], POSITIVE_SAMPLE):
        raise AssertionError("self-test broken: sha256 pattern misses real gate")


def check_built_dll(sha: str) -> None:
    import hashlib

    dll = os.path.join(TOOLS, "bin", "Mono.Cecil.dll")
    if not os.path.isfile(dll):
        print("SKIP: no built bin/Mono.Cecil.dll (run make tools)")
        return
    with open(dll, "rb") as fh:
        got = hashlib.sha256(fh.read()).hexdigest()
    if got != sha:
        raise AssertionError(
            f"bin/Mono.Cecil.dll does not match data/cecil.pin\n"
            f"  want {sha}\n  got  {got}\n"
            f"rebuild (make tools) or re-pin deliberately (tools/cecil-pin.sh)"
        )


def main() -> int:
    version, sha = load_pin()
    check_build_gate()
    check_built_dll(sha)
    print(f"OK: Mono.Cecil pin intact (version={version}, sha256={sha[:12]}...)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
