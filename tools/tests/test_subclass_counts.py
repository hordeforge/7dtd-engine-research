#!/usr/bin/env python3
"""Guard the leaf-count inventories against the DLL's concrete subclass counts.

Each per-leaf inventory (item-actions 38, sequence-requirements 38, ...)
counts the classes in a base's subclass closure (or a namespace for the
game-event actions), minus intermediate bases / sibling-namespace types per the
inventory's own stated convention. A game patch that adds/removes a leaf
without updating the inventory fails here.

Conventions encoded (verified against the current DLL):
- sequence-requirements: closure of GameEvent.SequenceRequirements.BaseRequirement
  = 38 (37 concrete leaves + the BaseOperationRequirement intermediate). The
  same-named Quests.Requirements.* and Challenges.BaseRequirementObjectiveGroup
  types are different bases and must NOT be counted (name-prefix matching does
  count them; full-name closure does not).
- item-actions: closure of ItemAction = 38 (37 concrete + ItemActionAttack, the
  only abstract member).
- quest-objectives / minevent-actions / block-behaviors: closures of
  BaseObjective / MinEventActionBase / Block = 38 / 71 / 65.
- sequence-actions: namespace GameEvent.SequenceActions has 132 classes (all
  concrete); BaseAction's closure is 136 (137 with the root), of which exactly
  5 live in sibling namespaces (SequenceDecisions/SequenceLoops); leaves = 132
  classes - 12 in-namespace base classes + 3 leaf-parents that are themselves
  listed = 123.

Usage: python3 tools/tests/test_subclass_counts.py [<asm>] (defaults to ASM env / standard install discovery)
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

REPO = str(_common.REPO)
INV = os.path.join(REPO, "docs", "inventories")

# (inventory, mode, target, expected, extra, self_state)
#   mode "closed": target is a base full name; expected is the closure total;
#   extra may be ("abstract", N) to lock the abstract-member count.
#   mode "seq": target is a namespace; expected is the leaf count derived as
#   namespace classes - in-namespace base classes + known leaf-parents.
#   self_state is the number the inventory text must state (defaults to
#   expected; differs for challenge-objectives, whose closure of 29 = 28 leaves
#   + the ChallengeBaseTrackedItemObjective intermediate).
CHECKS = [
    (
        "sequence-requirements.md",
        "closed",
        "GameEvent.SequenceRequirements.BaseRequirement",
        38,
        None,
        None,
    ),
    ("item-actions.md", "closed", "ItemAction", 38, ("abstract", 1), None),
    ("quest-objectives.md", "closed", "BaseObjective", 38, None, None),
    ("minevent-actions.md", "closed", "MinEventActionBase", 71, None, None),
    ("block-behaviors.md", "closed", "Block", 65, None, None),
    ("te-features.md", "closed", "TEFeatureAbs", 11, None, None),
    ("challenge-objectives.md", "closed", "Challenges.BaseChallengeObjective", 29, None, 28),
    ("sequence-actions.md", "seq", "GameEvent.SequenceActions", 123, None, None),
]

# Sibling-namespace members of the BaseAction closure (documented caveat).
SEQ_OUT_CLOSURE = [
    "GameEvent.SequenceDecisions.BaseDecision",
    "GameEvent.SequenceDecisions.DecisionIf",
    "GameEvent.SequenceLoops.BaseLoop",
    "GameEvent.SequenceLoops.LoopFor",
    "GameEvent.SequenceLoops.LoopWhile",
]
# SequenceActions leaves that parent one subclass each yet are still leaves.
SEQ_LEAF_PARENTS = ["ActionBlockReplace", "ActionRemoveEntities", "ActionSpawnEntity"]

SRC = r"""
using System;
using System.Linq;
using System.Collections.Generic;
using Mono.Cecil;
class SubCount {
  static string Full(TypeReference t) {
    return t == null ? "" : (t.Namespace.Length > 0 ? t.Namespace + "." + t.Name : t.Name);
  }
  static bool ClosedUnder(TypeDefinition t, string baseFullName) {
    var c = t.BaseType;
    while (c != null) {
      if (Full(c) == baseFullName) return true;
      var rb = c.Resolve();
      c = rb == null ? null : rb.BaseType;
    }
    return false;
  }
  static void Main(string[] a) {
    var r = new DefaultAssemblyResolver();
    r.AddSearchDirectory(System.IO.Path.GetDirectoryName(System.IO.Path.GetFullPath(a[0])));
    var asm = AssemblyDefinition.ReadAssembly(a[0], new ReaderParameters { AssemblyResolver = r });
    var types = asm.MainModule.GetTypes().ToList();
    foreach (var arg in a[1].Split(',')) {
      if (arg.StartsWith("closed:")) {
        string baseName = arg.Substring(7);
        var cl = types.Where(t => t.IsClass && ClosedUnder(t, baseName)).ToList();
        Console.WriteLine("closed {0} total={1} concrete={2} abstract={3}",
          baseName, cl.Count, cl.Count(t => !t.IsAbstract), cl.Count(t => t.IsAbstract));
      } else if (arg.StartsWith("seq:")) {
        string ns = arg.Substring(4);
        var inNs = types.Where(t => t.IsClass && t.Namespace == ns).ToList();
        var used = new HashSet<string>();
        foreach (var t in inNs) {
          var b = t.BaseType;
          while (b != null) {
            if (b.Namespace == ns) used.Add(b.Name);
            var rb = b.Resolve();
            b = rb == null ? null : rb.BaseType;
          }
        }
        string baseName = ns + ".BaseAction";
        var cl = types.Where(t => t.IsClass && ClosedUnder(t, baseName)).ToList();
        var outClosure = cl.Where(t => t.Namespace != ns).Select(t => Full(t)).OrderBy(x => x).ToList();
        Console.WriteLine("seq {0} total={1} concrete={2} abstract={3} usedbase={4} outclosure={5} closuretotal={6}",
          ns, inNs.Count, inNs.Count(t => !t.IsAbstract), inNs.Count(t => t.IsAbstract),
          string.Join("|", used.OrderBy(x => x)), string.Join("|", outClosure), cl.Count);
      }
    }
  }
}
"""


def main() -> int:
    asm_path, asm_label = _common.resolve_asm(sys.argv[1] if len(sys.argv) > 1 else None)
    if asm_path is None:
        print(f"SKIP: assembly not found: {asm_label}")
        return 0
    asm = str(asm_path)

    # key-methods fingerprint column (item-actions / minevent-actions): every
    # listed method must exist on the leaf type or its base chain
    meth_src = r"""
using System;
using System.Linq;
using Mono.Cecil;
class LeafMeth {
  static void Main(string[] a) {
    var r = new DefaultAssemblyResolver();
    r.AddSearchDirectory(System.IO.Path.GetDirectoryName(System.IO.Path.GetFullPath(a[0])));
    var asm = AssemblyDefinition.ReadAssembly(a[0], new ReaderParameters { AssemblyResolver = r });
    foreach (var t in asm.MainModule.GetTypes()) {
      var names = t.Methods.Select(m => m.Name).Distinct().OrderBy(x => x).ToList();
      Console.WriteLine(t.Name + "\t" + (t.BaseType == null ? "" : t.BaseType.Name) + "\t" + string.Join(",", names));
    }
  }
}
"""
    mout = _common.run_probe(_common.compile_probe(meth_src, "leafmeth_check"), asm)
    methods, base_of = {}, {}
    for line in mout.splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        methods[parts[0]] = set(parts[2].split(",")) if parts[2] else set()
        base_of[parts[0]] = parts[1]

    def has_method(typ, meth):
        seen = set()
        while typ and typ not in seen:
            seen.add(typ)
            if meth in methods.get(typ, set()):
                return True
            typ = base_of.get(typ, "")
        return False

    key_bad = []
    for inv in (
        "item-actions.md",
        "minevent-actions.md",
        "sequence-requirements.md",
        "quest-objectives.md",
        "block-behaviors.md",
        "challenge-objectives.md",
        "dedicated-leaves.md",
    ):
        text = open(os.path.join(INV, inv), encoding="utf-8").read()
        for m in re.finditer(r"^\| `([^`]+)` \| [^|]+ \| [^|]+ \| ([^|]+) \|", text, re.M):
            typ, kms = m.group(1), m.group(2)
            # dedicated-leaves mixes formats: skip rows whose fingerprint column
            # is a marker/prose or a referrer list (backticked type names)
            if any(x in kms for x in ("(fields only)", "(not found)", "(generic/nested", "`")):
                continue
            for km in [x.strip() for x in kms.split(",") if x.strip()]:
                km_name = km.split("(")[0].strip()
                if not has_method(typ, km_name):
                    key_bad.append(
                        f"{inv}: `{typ}` key method `{km_name}` (from `{km}`) not found on type or bases"
                    )

    args = [
        ",".join(
            ("closed:" if mode == "closed" else "seq:") + target
            for _, mode, target, _, _, _ in CHECKS
        )
    ]
    out = _common.run_probe(_common.compile_probe(SRC, "subcount_check"), asm, *args)
    stats = {}
    for line in out.splitlines():
        parts = line.split()
        if parts[0] == "closed":
            d = dict(kv.split("=") for kv in parts[2:])
            d["total"] = int(d["total"])
            d["concrete"] = int(d["concrete"])
            d["abstract"] = int(d["abstract"])
            stats[parts[1]] = d
        elif parts[0] == "seq":
            d = dict(kv.split("=") for kv in parts[2:])
            d["total"] = int(d["total"])
            d["concrete"] = int(d["concrete"])
            d["abstract"] = int(d["abstract"])
            d["usedbase"] = d["usedbase"].split("|") if d["usedbase"] else []
            d["outclosure"] = d["outclosure"].split("|") if d["outclosure"] else []
            d["closuretotal"] = int(d["closuretotal"])
            stats[parts[1]] = d
    bad = []
    for inventory, mode, target, expected, extra, self_state in CHECKS:
        d = stats[target]
        if mode == "closed":
            if d["total"] != expected:
                bad.append(
                    f"{inventory}: closure of {target} = {d['total']} (concrete {d['concrete']}, abstract {d['abstract']}) != stated {expected}"
                )
            if extra and d[extra[0]] != extra[1]:
                bad.append(f"{inventory}: {target} {extra[0]} count = {d[extra[0]]} != {extra[1]}")
        else:
            leaf_parents = [n for n in SEQ_LEAF_PARENTS if n in d["usedbase"]]
            leaves = d["total"] - len(d["usedbase"]) + len(leaf_parents)
            if leaves != expected:
                bad.append(
                    f"{inventory}: derived leaves = {leaves} (ns {d['total']} - {len(d['usedbase'])} bases + {len(leaf_parents)} leaf-parents) != stated {expected}"
                )
            if d["abstract"] != 0:
                bad.append(
                    f"{inventory}: namespace has {d['abstract']} abstract classes, expected 0"
                )
            if d["closuretotal"] != d["total"] - 1 + len(d["outclosure"]):
                bad.append(
                    f"{inventory}: BaseAction closure = {d['closuretotal']}, expected {d['total'] - 1 + len(d['outclosure'])} (ns {d['total']} - root + {len(d['outclosure'])} out-of-ns)"
                )
            if d["outclosure"] != SEQ_OUT_CLOSURE:
                bad.append(
                    f"{inventory}: out-of-namespace closure {d['outclosure']} != documented {SEQ_OUT_CLOSURE}"
                )
            if len(leaf_parents) != len(SEQ_LEAF_PARENTS):
                bad.append(
                    f"{inventory}: leaf-parents used as bases = {leaf_parents}, expected all of {SEQ_LEAF_PARENTS}"
                )
        # the inventory must self-state the count (leaves for challenge-objectives)
        text = open(os.path.join(INV, inventory), encoding="utf-8").read()
        stated = self_state if self_state is not None else expected
        if not re.search(rf"\b{stated}\b", text):
            bad.append(f"{inventory}: does not self-state {stated}")
    if bad:
        for b in bad:
            print("FAIL:", b)
        return 1
    if key_bad:
        for b in key_bad:
            print("FAIL:", b)
        return 1
    print(
        f"OK: {len(CHECKS)} leaf inventories consistent with the DLL, key-method fingerprints valid"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
