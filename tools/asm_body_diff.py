#!/usr/bin/env python3
"""Pairwise method-body hash diff of two Assembly-CSharp.dll builds.

Hashes every method body via Mono.Cecil (same Mono.Cecil as tools/bin) and
reports added / removed / body-changed methods. Catches same-size IL rewrites
that FullSurface type-row diffs miss.

Usage:
  python3 tools/asm_body_diff.py <old.dll> <new.dll>
  python3 tools/asm_body_diff.py --help

Requires mono + tools/bin/Mono.Cecil.dll (built by `make tools`).
"""

from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
CECIL = TOOLS / "bin" / "Mono.Cecil.dll"
HASH_CS = r"""
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using Mono.Cecil;

static class AsmBodyDiff {
  static string Key(MethodDefinition m) => m.DeclaringType.FullName + "::" + m.FullName;
  static string Hex16(byte[] b) {
    var sb = new StringBuilder(32);
    for (int i = 0; i < 8 && i < b.Length; i++) sb.Append(b[i].ToString("x2"));
    return sb.ToString();
  }
  static string Hash(MethodDefinition m) {
    if (!m.HasBody) return "-";
    var ms = new MemoryStream();
    foreach (var i in m.Body.Instructions) {
      var op = BitConverter.GetBytes((int)i.OpCode.Code);
      ms.Write(op, 0, op.Length);
      if (i.Operand is MethodReference mr) {
        var s = Encoding.UTF8.GetBytes(mr.FullName); ms.Write(s, 0, s.Length);
      } else if (i.Operand is FieldReference fr) {
        var s = Encoding.UTF8.GetBytes(fr.FullName); ms.Write(s, 0, s.Length);
      } else if (i.Operand is string str) {
        var s = Encoding.UTF8.GetBytes(str); ms.Write(s, 0, s.Length);
      } else if (i.Operand is int iv) {
        var b = BitConverter.GetBytes(iv); ms.Write(b, 0, b.Length);
      } else if (i.Operand is long lv) {
        var b = BitConverter.GetBytes(lv); ms.Write(b, 0, b.Length);
      } else if (i.Operand is float fv) {
        var b = BitConverter.GetBytes(fv); ms.Write(b, 0, b.Length);
      } else if (i.Operand is double dv) {
        var b = BitConverter.GetBytes(dv); ms.Write(b, 0, b.Length);
      } else if (i.Operand is TypeReference tr) {
        var s = Encoding.UTF8.GetBytes(tr.FullName); ms.Write(s, 0, s.Length);
      }
    }
    return Hex16(SHA256.Create().ComputeHash(ms.ToArray()));
  }
  static Dictionary<string,string> Map(string path) {
    var d = new Dictionary<string,string>();
    var asm = AssemblyDefinition.ReadAssembly(path);
    foreach (var t in asm.MainModule.GetTypes())
      foreach (var m in t.Methods)
        d[Key(m)] = Hash(m) + "\t" + (m.HasBody ? m.Body.Instructions.Count.ToString() : "0");
    return d;
  }
  static void Main(string[] args) {
    var a = Map(args[0]); var b = Map(args[1]);
    var added = b.Keys.Except(a.Keys).OrderBy(x => x).ToList();
    var removed = a.Keys.Except(b.Keys).OrderBy(x => x).ToList();
    var changed = a.Keys.Intersect(b.Keys).Where(k => a[k] != b[k]).OrderBy(k => k).ToList();
    Console.WriteLine($"methods bak={a.Count} live={b.Count} added={added.Count} removed={removed.Count} body-changed={changed.Count}");
    foreach (var x in added) Console.WriteLine(" + " + x + " " + b[x]);
    foreach (var x in removed) Console.WriteLine(" - " + x + " " + a[x]);
    foreach (var k in changed) Console.WriteLine(" ~ " + k + " " + a[k] + " -> " + b[k]);
  }
}
"""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Hash-diff every method body between two managed assemblies."
    )
    ap.add_argument("old_dll", nargs="?", help="baseline Assembly-CSharp.dll")
    ap.add_argument("new_dll", nargs="?", help="candidate Assembly-CSharp.dll")
    args = ap.parse_args()
    if not args.old_dll or not args.new_dll:
        ap.print_help()
        return 2 if args.old_dll or args.new_dll else 0

    old = Path(args.old_dll)
    new = Path(args.new_dll)
    if not old.is_file() or not new.is_file():
        print(f"asm_body_diff: missing dll: old={old} new={new}", file=sys.stderr)
        return 2
    if not CECIL.is_file():
        print(
            f"asm_body_diff: missing {CECIL}; run `make tools` first",
            file=sys.stderr,
        )
        return 2

    # Stamp both inputs: a body-hash report is only meaningful next to the exact
    # bytes it compared, and the sha256 is what tools/data/steam_builds.json maps
    # back to a Steam build id.
    for label, path in (("old", old), ("new", new)):
        print(f"# {label} {path} bytes={path.stat().st_size} sha256={sha256(path)}")

    with tempfile.TemporaryDirectory(prefix="asm_body_diff_") as tmp:
        tmp_path = Path(tmp)
        cs = tmp_path / "AsmBodyDiff.cs"
        exe = tmp_path / "AsmBodyDiff.exe"
        cs.write_text(HASH_CS, encoding="utf-8")
        compile_cmd = ["mcs", f"-r:{CECIL}", f"-out:{exe}", str(cs)]
        comp = subprocess.run(compile_cmd, text=True, capture_output=True)
        if comp.returncode != 0:
            print(comp.stderr or comp.stdout, file=sys.stderr)
            return 1
        env = os.environ.copy()
        env["MONO_PATH"] = str(TOOLS / "bin")
        run = subprocess.run(
            ["mono", str(exe), str(old), str(new)],
            text=True,
            capture_output=True,
            env=env,
        )
        if run.returncode != 0:
            print(run.stderr or run.stdout, file=sys.stderr)
            return 1
        sys.stdout.write(run.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
