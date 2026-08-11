#!/usr/bin/env python3
"""Guard the AI-director horde constants documented in aidirector.md against the DLL.

The tuned blood-moon party / wandering-horde numbers (join/sight/teleport
distances, spawn geometry, party enemy max, scheduling gates) are const fields
in the AIDirector* classes. A game patch that retunes them without updating the
doc fails here.

Usage: python3 tools/tests/test_horde_constants.py <asm>
"""
import os
import re
import subprocess
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(TOOLS)
DOC = os.path.join(REPO, "docs", "aidirector.md")

# class -> { const name: expected value } (values from the V3.1.0 DLL)
CONSTS = {
    "AIDirectorBloodMoonParty": {
        "cPartyJoinDistance": 80,
        "cPartyJoinDistanceSq": 6400,
        "cSightDist": 100,
        "cSightDistSq": 10000,
        "cSpawnAngle": 90,
        "cSpawnDistance": 40,
        "cSpawnMaxRandDistance": 10,
        "cSpawnMinPlayerDistance": 30,
        "cSpawnMinRandDistance": 0,
        "cSpawnPreferredArc": 120,
        "cTeleportDist": 150,
        "cTeleportDistSq": 22500,
    },
    "AIDirectorBloodMoonComponent": {
        "cPartyEnemyMax": 30,
        "cSpawnDelay": 1,
        "cTimeStayAfterDeathScale": 3,
    },
    "AIDirectorWanderingHordeComponent": {
        "cNextHourMin": 7,
    },
    "AIWanderingHordeSpawner": {
        "cInvestigateTime": 6000,
    },
    "AIDirectorChunkData": {
        "cCooldownDelay": 240,
        "cCooldownLongDelay": 1320,
        "cCooldownNeighborDelay": 180,
        "cCooldownNeighborLongDelay": 720,
        "cVersion": 2,
    },
    "AIDirectorChunkEventComponent": {
        "cActivityLevelToSpawn": 25,
        "cEventDelay": 5,
        "cSpawnChance": 0.2,
        "cVersion": 1,
    },
    "AIDirectorHordeComponent": {
        "cPitstopSideMin": 40,
        "cPitstopSideRange": 20,
        "cPlayerClosestDist": 30,
        "cSinglePlayerSkipPer": 0.3,
    },
    "AIDirectorPlayerState": {
        "kCheckUndergroundTime": 5,
        "kNumBlocksUnderground": 10,
    },
    "AIDirectorSmellMarker": {
        "kMax": 256,
    },
    "AIDirector": {
        "cActivityDuration": 720,
        "cActivityNoiseDuration": 240,
    },
}

SRC = r"""
using System;
using System.Linq;
using Mono.Cecil;
class HordeConsts {
  static void Main(string[] a) {
    var r = new DefaultAssemblyResolver();
    r.AddSearchDirectory(System.IO.Path.GetDirectoryName(System.IO.Path.GetFullPath(a[0])));
    var asm = AssemblyDefinition.ReadAssembly(a[0], new ReaderParameters { AssemblyResolver = r });
    foreach (var tn in a[1].Split(',')) {
      var t = asm.MainModule.GetTypes().FirstOrDefault(x => x.Name == tn);
      if (t == null) continue;
      foreach (var f in t.Fields.Where(f => f.HasConstant))
        Console.WriteLine(tn + "." + f.Name + "=" + f.Constant);
    }
  }
}
"""
EXE = "/tmp/hordeconsts_check.exe"


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: test_horde_constants.py <asm>", file=sys.stderr)
        return 2
    asm = sys.argv[1]
    src = "/tmp/hordeconsts_check.cs"
    with open(src, "w") as f:
        f.write(SRC)
    subprocess.run(
        ["mcs", "-r:%s" % os.path.join(TOOLS, "bin", "Mono.Cecil.dll"), src, "-out:" + EXE],
        check=True,
    )
    env = dict(os.environ)
    env["MONO_PATH"] = os.path.join(TOOLS, "bin")
    out = subprocess.run(
        ["mono", EXE, asm, ",".join(CONSTS)], capture_output=True, text=True, env=env, check=True,
    ).stdout
    dll = {}
    for line in out.splitlines():
        cls, _, rest = line.partition(".")
        name, _, val = rest.partition("=")
        dll[(cls, name)] = val

    doc = open(DOC, encoding="utf-8").read()
    bad = []
    for cls, consts in CONSTS.items():
        for name, want in consts.items():
            have = dll.get((cls, name))
            if have is None:
                bad.append(f"{cls}.{name}: missing from DLL")
            elif have != str(want):
                bad.append(f"{cls}.{name}: DLL {have} != expected {want}")
            # the doc must state the name (and ideally the value); the derived
            # *Sq constants are documented by value only ("(sq 6400)")
            if not name.endswith("Sq") and not re.search(rf"`?{name}`?", doc):
                bad.append(f"aidirector.md: does not mention {name}")
            if str(want) not in doc:
                bad.append(f"aidirector.md: does not state {want} (for {name})")
    if bad:
        for b in bad[:20]:
            print("FAIL:", b)
        if len(bad) > 20:
            print(f"...and {len(bad) - 20} more")
        return 1
    n = sum(len(v) for v in CONSTS.values())
    print(f"OK: {n} horde constants pinned in the DLL and stated in aidirector.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
