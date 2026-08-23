#!/usr/bin/env python3
"""Guard the console client-executable / dedicated-gate classification.

console-commands.md 6 states the machine-swept split of the 188-command
population (CmdMap.exe rows): how many leaves carry get_IsExecuteOnClient=true,
how many start Execute with a GameManager.IsDedicatedServer gate, and the exact
10 dedicated-gated class names. A game patch that adds or removes a client
toggle or a dedicated gate without updating the doc fails here.

Usage: python3 tools/tests/test_console_classification.py <asm>
"""
import atexit
import os
import re
import shutil
import subprocess
import sys
import tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(TOOLS)
DOC = os.path.join(REPO, "docs", "console-commands.md")
BIN = os.path.join(TOOLS, "bin")
XREF = os.path.join(BIN, "CmdMap.exe")

# The 10 dedicated-gated leaves, as documented (console-commands.md 6).
GATED = [
    "ConsoleCmdChallenges", "ConsoleCmdGiveQualityItem", "ConsoleCmdGiveQuest",
    "ConsoleCmdOcclusion", "ConsoleCmdPathTest", "ConsoleCmdRemoveQuest",
    "ConsoleCmdResetAchievementStats", "ConsoleCmdSelfExp",
    "ConsoleCmdSpectatorMode", "ConsoleCmdSpectrum",
]

SRC = r"""
using System;
using System.Linq;
using System.Collections.Generic;
using System.IO;
using Mono.Cecil;
using Mono.Cecil.Cil;
class Cls {
  static void Main(string[] a) {
    var asm = AssemblyDefinition.ReadAssembly(a[0]);
    var names = File.ReadAllLines(a[1]).Skip(1).Select(l => l.Split('\t')[1]).Distinct().ToList();
    int onClient = 0, dediGate = 0, either = 0;
    var gated = new List<string>();
    foreach (var n in names) {
      var t = asm.MainModule.GetTypes().FirstOrDefault(x => x.Name == n);
      if (t == null) continue;
      var exec = t.Methods.FirstOrDefault(m => m.Name == "Execute" && m.HasBody);
      if (exec == null) continue;
      var io = t.Methods.FirstOrDefault(m => m.Name == "get_IsExecuteOnClient" && m.HasBody);
      bool oc = io != null && io.Body.Instructions.Any(i => i.OpCode.Code == Code.Ldc_I4_1);
      bool dg = exec.Body.Instructions.Take(6).Any(i => i.OpCode.Code == Code.Call && i.Operand != null && i.Operand.ToString().Contains("get_IsDedicatedServer"));
      if (oc) onClient++;
      if (dg) { dediGate++; gated.Add(n); }
      if (oc || dg) either++;
    }
    Console.WriteLine("leaves=" + names.Count + " onClient=" + onClient + " dediGate=" + dediGate + " either=" + either);
    foreach (var g in gated.OrderBy(x => x)) Console.WriteLine("GATED " + g);
  }
}
"""
# Private scratch dir: a fixed /tmp name for a probe we compile and execute
# would let any local user pre-create or symlink it.
SCRATCH = tempfile.mkdtemp(prefix="console-classification-")
atexit.register(shutil.rmtree, SCRATCH, True)
EXE = os.path.join(SCRATCH, "console_classification_check.exe")


def main() -> int:
    if len(sys.argv) < 2 or not os.path.exists(sys.argv[1]):
        print("SKIP: no ASM path (or missing file); pass <asm>")
        return 0
    if not os.path.exists(XREF):
        print("SKIP: CmdMap.exe not built (run make tools)")
        return 0
    asm = sys.argv[1]

    if not os.path.exists(EXE):
        src = os.path.join(SCRATCH, "console_classification_check.cs")
        with open(src, "w", encoding="utf-8") as f:
            f.write(SRC)
        # The probe links Mono.Cecil; mono needs MONO_PATH to load it at runtime.
        r = subprocess.run(["csc", "-r:" + os.path.join(BIN, "Mono.Cecil.dll"), src,
                            "-out:" + EXE], capture_output=True, text=True)
        if r.returncode != 0:
            print("FAIL: csc compile error: " + r.stderr[:500])
            return 1

    env = dict(os.environ, MONO_PATH=BIN)
    r = subprocess.run(["mono", XREF, asm], capture_output=True, text=True)
    if r.returncode != 0:
        print("FAIL: CmdMap.exe error")
        return 1
    mapf = os.path.join(SCRATCH, "cmdmap_classify.txt")
    with open(mapf, "w", encoding="utf-8") as f:
        f.write(r.stdout)

    r = subprocess.run(["mono", EXE, asm, mapf], capture_output=True, text=True, env=env)
    out = r.stdout
    m = re.search(r"leaves=(\d+) onClient=(\d+) dediGate=(\d+) either=(\d+)", out)
    if not m:
        print("FAIL: probe output unparsable: " + out[:300])
        return 1
    leaves, on_client, dedi, either = (int(m.group(i)) for i in range(1, 5))
    gated = sorted(l.split(" ", 1)[1] for l in out.splitlines() if l.startswith("GATED "))

    doc = open(DOC, encoding="utf-8").read()
    bad = []
    if leaves != 188:
        bad.append(f"console population {leaves} != 188 (CmdMap rows)")
    if "84 of the 188 leaves" not in doc:
        bad.append("doc no longer states '84 of the 188 leaves'")
    if on_client != 83:
        bad.append(f"onClient {on_client} != 83 (doc 83)")
    if either != 84:
        bad.append(f"either {either} != 84 (doc 84)")
    if gated != GATED:
        bad.append(f"dedicated-gated set mismatch: doc {GATED} vs DLL {gated}")
    if bad:
        for b in bad:
            print("FAIL: " + b)
        return 1
    print(f"OK: console classification (188 leaves; 83 client-exec, {either} either, {dedi} gated) matches the doc")
    return 0


if __name__ == "__main__":
    sys.exit(main())
