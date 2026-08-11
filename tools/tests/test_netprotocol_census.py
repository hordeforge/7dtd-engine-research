#!/usr/bin/env python3
"""Guard the NetProtocolCensus claims in protocol-packages.md against the live DLL.

The doc claims "exactly 6 packages override to channel 1" and names them.
NetProtocolCensus.exe re-derives the per-package channel census; a package that
moves channels, or a census the doc mis-states, fails here.

Usage: python3 tools/tests/test_netprotocol_census.py <asm>
"""
import os
import re
import subprocess
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(TOOLS)
DOC = os.path.join(REPO, "docs", "protocol-packages.md")
NPC = os.path.join(TOOLS, "bin", "NetProtocolCensus.exe")

CHANNEL1 = [
    "NetPackageChunk",
    "NetPackageChunkRemove",
    "NetPackageMapChunks",
    "NetPackageDynamicMesh",
    "NetPackagePOIAround",
    "NetPackageWorldFolder",
]
COMPRESSED = [
    "NetPackageChunk",
    "NetPackageMapChunks",
    "NetPackageDynamicMesh",
    "NetPackagePOIAround",
    "NetPackageConfigFile",
    "NetPackageDynamicClientArrive",
    "NetPackageIdMapping",
    "NetPackageSignDataResponse",
]
EXPECTED_TOTAL = 193


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: test_netprotocol_census.py <asm>", file=sys.stderr)
        return 2
    asm = sys.argv[1]
    env = dict(os.environ)
    env["MONO_PATH"] = os.path.join(TOOLS, "bin")
    out = subprocess.run(
        ["mono", NPC, asm, "/tmp/npc_check_META.md"],
        capture_output=True, text=True, env=env,
    )
    meta = open("/tmp/npc_check_META.md", encoding="utf-8").read() if os.path.exists("/tmp/npc_check_META.md") else ""
    if not meta:
        print("FAIL: NetProtocolCensus produced no output", file=sys.stderr)
        return 1
    chan1 = set()
    compressed = set()
    total = 0
    for line in meta.splitlines()[2:]:
        parts = [c.strip() for c in line.split("|")]
        if len(parts) < 4 or not parts[1].startswith("NetPackage"):
            continue
        total += 1
        if parts[2] == "1":
            chan1.add(parts[1])
        if parts[3] == "1":
            compressed.add(parts[1])
    doc = open(DOC, encoding="utf-8").read()
    bad = []
    if total != EXPECTED_TOTAL:
        bad.append(f"census rows = {total}, expected {EXPECTED_TOTAL}")
    if chan1 != set(CHANNEL1):
        bad.append(f"channel-1 packages {sorted(chan1)} != documented {CHANNEL1}")
    if compressed != set(COMPRESSED):
        bad.append(f"compressed packages {sorted(compressed)} != documented {COMPRESSED}")
    if not re.search(r"[Ee]xactly \*{0,2}6\*{0,2} override", doc):
        bad.append("protocol-packages.md: no 'exactly 6 override to channel 1' claim")
    if not re.search(r"\*\*8 packages\*\*", doc):
        bad.append("protocol-packages.md: no '**8 packages set get_Compress = 1**' claim")
    for p in CHANNEL1 + COMPRESSED:
        if not re.search(rf"`{p}`", doc):
            bad.append(f"protocol-packages.md: does not mention `{p}`")
    if bad:
        for b in bad:
            print("FAIL:", b)
        return 1
    print(f"OK: census {total} packages; exactly {len(chan1)} on channel 1 and {len(compressed)} compressed, matching the doc")
    return 0


if __name__ == "__main__":
    sys.exit(main())
