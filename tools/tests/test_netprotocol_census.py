#!/usr/bin/env python3
"""Guard the NetProtocolCensus claims in protocol-packages.md against the live DLL.

The doc claims "exactly 6 packages override to channel 1" and names them.
NetProtocolCensus.exe re-derives the per-package channel census; a package that
moves channels, or a census the doc mis-states, fails here.

Usage: python3 tools/tests/test_netprotocol_census.py <asm>
"""

import os
import re
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(TOOLS)
DOC = os.path.join(REPO, "docs", "protocol-packages.md")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

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
# packages that explicitly override Delivery to unreliable (0); all others keep
# the reliable default (network.md §5)
UNRELIABLE = [
    "NetPackageEntityPosAndRot",
    "NetPackageEntityRelPosAndRot",
    "NetPackageEntityRotation",
    "NetPackageEntitySpeeds",
    "NetPackageEntityStatsBuff",
]
# packages that override AllowedBeforeAuth to true (the pre-auth handshake set;
# the base NetPackage getter returns false, network.md §5)
ALLOWED_BEFORE_AUTH = [
    "NetPackagePlayerLogin",
    "NetPackagePlayerDenied",
    "NetPackagePackageIds",
    "NetPackageKeyExchangeComplete",
    "NetPackageEncryptionRequest",
    "NetPackageEncryptionPublicKey",
    "NetPackageEncryptionSharedKey",
    "NetPackageEAC",
    "NetPackageAuthState",
    "NetPackageAuthConfirmation",
]
# the 4 top-level NetPackage* types that are NOT registered wire packages
# (193 top-level - 4 = 189 in the live id-map; network.md §3)
NON_MAP = [
    "NetPackage",  # abstract base
    "NetPackageDirection",  # enum
    "NetPackageEntityTargeted",  # abstract intermediate
    "NetPackageLogger",  # abstract helper
]
EXPECTED_TOTAL = 193


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: test_netprotocol_census.py <asm>", file=sys.stderr)
        return 2
    asm = sys.argv[1]
    meta_path = str(_common.probe_dir() / "npc_check_META.md")
    rc_census, _out, census_err = _common.run_tool("NetProtocolCensus.exe", asm, meta_path)
    if rc_census != 0:
        # A crashed census must read as a tool failure: a partial table would
        # otherwise parse as wrong counts and masquerade as doc drift.
        print(
            f"FAIL: NetProtocolCensus.exe exited {rc_census}: {census_err.strip()[:300]}",
            file=sys.stderr,
        )
        return 1
    meta = open(meta_path, encoding="utf-8").read() if os.path.exists(meta_path) else ""
    if not meta:
        print("FAIL: NetProtocolCensus produced no output", file=sys.stderr)
        return 1
    chan1 = set()
    compressed = set()
    unreliable = set()
    allowed_before_auth = set()
    total = 0
    for line in meta.splitlines()[2:]:
        parts = [c.strip() for c in line.split("|")]
        if len(parts) < 7 or not parts[1].startswith("NetPackage"):
            continue
        total += 1
        if parts[2] == "1":
            chan1.add(parts[1])
        if parts[3] == "1":
            compressed.add(parts[1])
        if parts[5] == "0":
            unreliable.add(parts[1])
        if parts[6] == "1":
            allowed_before_auth.add(parts[1])
    # kind (abstract/enum) of the top-level NetPackage* types - the 4 non-map
    # helpers (the META has no kind column)
    kind_src = r"""
using System;
using System.Linq;
using Mono.Cecil;
class NpKind {
  static void Main(string[] a) {
    var asm = AssemblyDefinition.ReadAssembly(a[0]);
    foreach (var t in asm.MainModule.Types.Where(t => t.Name.StartsWith("NetPackage") && t.Name != "NetPackageManager")) {
      if (t.IsAbstract) Console.WriteLine(t.Name + "\tABSTRACT");
      else if (t.IsEnum) Console.WriteLine(t.Name + "\tENUM");
    }
  }
}
"""
    kind_exe = _common.compile_probe(kind_src, "npkind_check")
    kout = _common.run_probe(kind_exe, asm)
    non_map = set()
    for line in kout.splitlines():
        name, _, _kind = line.partition("\t")
        non_map.add(name)
    doc = open(DOC, encoding="utf-8").read()
    bad = []
    if total != EXPECTED_TOTAL:
        bad.append(f"census rows = {total}, expected {EXPECTED_TOTAL}")
    if chan1 != set(CHANNEL1):
        bad.append(f"channel-1 packages {sorted(chan1)} != documented {CHANNEL1}")
    if compressed != set(COMPRESSED):
        bad.append(f"compressed packages {sorted(compressed)} != documented {COMPRESSED}")
    if allowed_before_auth != set(ALLOWED_BEFORE_AUTH):
        bad.append(
            f"allowed-before-auth packages {sorted(allowed_before_auth)} != documented {ALLOWED_BEFORE_AUTH}"
        )
    if unreliable != set(UNRELIABLE):
        bad.append(f"unreliable packages {sorted(unreliable)} != documented {UNRELIABLE}")
    if non_map != set(NON_MAP):
        bad.append(f"non-map packages {sorted(non_map)} != expected {NON_MAP}")
    # network.md §3 must state the 189-in-map / 4-helpers accounting
    net = open(os.path.join(REPO, "docs", "network.md"), encoding="utf-8").read()
    if "**189**" not in net:
        bad.append("network.md: no '**189**' live id-map claim")
    if "remaining **4**" not in net:
        bad.append("network.md: no 'remaining **4**' helper claim")
    for p in NON_MAP:
        if not re.search(rf"`{p}`", net):
            bad.append(f"network.md: does not name helper `{p}`")
    if not re.search(r"[Ee]xactly \*{0,2}6\*{0,2} override", doc):
        bad.append("protocol-packages.md: no 'exactly 6 override to channel 1' claim")
    if not re.search(r"\*\*8 packages set", doc):
        bad.append("protocol-packages.md: no '**8 packages set get_Compress = 1**' claim")
    for p in CHANNEL1 + COMPRESSED + ALLOWED_BEFORE_AUTH + UNRELIABLE:
        if not re.search(rf"`{p}`", doc):
            bad.append(f"protocol-packages.md: does not mention `{p}`")
    if bad:
        for b in bad:
            print("FAIL:", b)
        return 1
    print(
        f"OK: census {total} packages; {len(chan1)} channel-1, {len(compressed)} compressed, {len(unreliable)} unreliable, {len(allowed_before_auth)} allowed-before-auth, {len(non_map)} non-map - all match the doc"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
