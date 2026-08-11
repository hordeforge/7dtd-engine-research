#!/usr/bin/env python3
"""Guard tuned game constants documented in the docs against the DLL.

The AI-director horde/placement/scheduling constants and the water-sim constants
are const fields in the game classes. A game patch that retunes them without
updating the doc fails here. The doc-side check requires the constant name and
value to appear in the owning doc (derived *Sq constants are value-only).

Usage: python3 tools/tests/test_tuned_constants.py <asm>
"""
import os
import re
import subprocess
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(TOOLS)
DOCS = os.path.join(REPO, "docs")

# family -> (doc, { const name: expected value })  (values from the V3.1.0 DLL)
CONSTS = {
    "AIDirectorBloodMoonParty": ("aidirector.md", {
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
    }),
    "AIDirectorBloodMoonComponent": ("aidirector.md", {
        "cPartyEnemyMax": 30,
        "cSpawnDelay": 1,
        "cTimeStayAfterDeathScale": 3,
    }),
    "AIDirectorWanderingHordeComponent": ("aidirector.md", {
        "cNextHourMin": 7,
    }),
    "AIWanderingHordeSpawner": ("aidirector.md", {
        "cInvestigateTime": 6000,
    }),
    "AIDirectorChunkData": ("aidirector.md", {
        "cCooldownDelay": 240,
        "cCooldownLongDelay": 1320,
        "cCooldownNeighborDelay": 180,
        "cCooldownNeighborLongDelay": 720,
        "cVersion": 2,
    }),
    "AIDirectorChunkEventComponent": ("aidirector.md", {
        "cActivityLevelToSpawn": 25,
        "cEventDelay": 5,
        "cSpawnChance": 0.2,
        "cVersion": 1,
    }),
    "AIDirectorHordeComponent": ("aidirector.md", {
        "cPitstopSideMin": 40,
        "cPitstopSideRange": 20,
        "cPlayerClosestDist": 30,
        "cSinglePlayerSkipPer": 0.3,
    }),
    "AIDirectorPlayerState": ("aidirector.md", {
        "kCheckUndergroundTime": 5,
        "kNumBlocksUnderground": 10,
    }),
    "AIDirectorSmellMarker": ("aidirector.md", {
        "kMax": 256,
    }),
    "AIDirector": ("aidirector.md", {
        "cActivityDuration": 720,
        "cActivityNoiseDuration": 240,
    }),
    "BlockLiquidv2": ("light-mesh-water.md", {
        "MAX_EMISSIONS": 3,
        "blockUpdatesPerSecond": 16,
        "AUTO_GENERATED": 8,
        "ZERO_EMISSIONS": 0,
        "ZERO_EVAPORATION": 0,
    }),
}

SRC = r"""
using System;
using System.Linq;
using Mono.Cecil;
using Mono.Cecil.Cil;
class TunedConsts {
  static void Main(string[] a) {
    var r = new DefaultAssemblyResolver();
    r.AddSearchDirectory(System.IO.Path.GetDirectoryName(System.IO.Path.GetFullPath(a[0])));
    var asm = AssemblyDefinition.ReadAssembly(a[0], new ReaderParameters { AssemblyResolver = r });
    foreach (var tn in a[1].Split(',')) {
      var t = asm.MainModule.GetTypes().FirstOrDefault(x => x.Name == tn);
      if (t == null) continue;
      foreach (var f in t.Fields.Where(f => f.HasConstant))
        Console.WriteLine(tn + "." + f.Name + "=" + f.Constant);
      // static fields initialized in the .cctor (ldc/ldstr + stsfld)
      var cctor = t.Methods.FirstOrDefault(x => x.Name == ".cctor" && x.HasBody);
      if (cctor != null) {
        var ins = cctor.Body.Instructions;
        for (int i = 0; i < ins.Count - 1; i++) {
          if (ins[i + 1].OpCode.Code == Code.Stsfld) {
            var fr = ins[i + 1].Operand as FieldReference;
            if (fr != null && fr.DeclaringType.Name == tn) {
              object val = null;
              var c = ins[i].OpCode.Code;
              if (c == Code.Ldc_I4 || c == Code.Ldc_I4_S || c == Code.Ldc_R4 || c == Code.Ldstr)
                val = ins[i].Operand;
              else if (c >= Code.Ldc_I4_0 && c <= Code.Ldc_I4_8)
                val = (int)(c - Code.Ldc_I4_0);
              else if (c == Code.Ldc_I4_M1)
                val = -1;
              if (val != null)
                Console.WriteLine(tn + "." + fr.Name + "=" + val);
            }
          }
        }
      }
    }
  }
}
"""
EXE = "/tmp/tunedconsts_check.exe"


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: test_tuned_constants.py <asm>", file=sys.stderr)
        return 2
    asm = sys.argv[1]
    src = "/tmp/tunedconsts_check.cs"
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

    bad = []
    for cls, (doc_name, consts) in CONSTS.items():
        doc = open(os.path.join(DOCS, doc_name), encoding="utf-8").read()
        for name, want in consts.items():
            have = dll.get((cls, name))
            if have is None:
                bad.append(f"{cls}.{name}: missing from DLL")
            elif have != str(want):
                bad.append(f"{cls}.{name}: DLL {have} != expected {want}")
            # the doc must state the name (and ideally the value); derived *Sq
            # constants are documented by value only ("(sq 6400)")
            if not name.endswith("Sq") and not re.search(rf"`?{name}`?", doc):
                bad.append(f"{doc_name}: does not mention {name}")
            if str(want) not in doc:
                bad.append(f"{doc_name}: does not state {want} (for {name})")
    if bad:
        for b in bad[:25]:
            print("FAIL:", b)
        if len(bad) > 25:
            print(f"...and {len(bad) - 25} more")
        return 1
    n = sum(len(d) for _, d in CONSTS.values())
    print(f"OK: {n} tuned constants pinned in the DLL and stated in the docs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
