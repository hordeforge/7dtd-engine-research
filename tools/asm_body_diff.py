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
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tooling

TOOLS = Path(__file__).resolve().parent
CECIL = TOOLS / "bin" / "Mono.Cecil.dll"
HASH_CS = r"""
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Threading;
using Mono.Cecil;

// One BodyHasher per thread. The hasher owns its buffer, scratch array and
// SHA256 instance, so the two assembly walks run concurrently without shared
// mutable state (the earlier static form raced and corrupted the stream).
//
// Zero-allocation hashing on the hot path: one reusable buffer and one SHA256
// instance per assembly for all ~56k methods, so the per-instruction
// BitConverter/UTF8/ToArray allocations (millions of them, ~44e9 instructions
// retired on the 3.2.0 pair) disappear. The byte stream per method is unchanged,
// so hashes still match any pre-optimization report.
class BodyHasher {
  static readonly char[] HexDigits = "0123456789abcdef".ToCharArray();
  readonly MemoryStream Buf = new MemoryStream(1 << 16);
  readonly SHA256 Sha = SHA256.Create();
  readonly Encoding Utf8 = new UTF8Encoding(false);
  byte[] Scratch = new byte[256];

  public static string Key(MethodDefinition m) => m.DeclaringType.FullName + "::" + m.FullName;

  string Hex16(byte[] b) {
    var c = new char[16];
    for (int i = 0; i < 8; i++) {
      c[i * 2] = HexDigits[b[i] >> 4];
      c[i * 2 + 1] = HexDigits[b[i] & 15];
    }
    return new string(c);
  }
  void WInt(int v) {
    Scratch[0] = (byte)v; Scratch[1] = (byte)(v >> 8);
    Scratch[2] = (byte)(v >> 16); Scratch[3] = (byte)(v >> 24);
    Buf.Write(Scratch, 0, 4);
  }
  void WLong(long v) {
    for (int i = 0; i < 8; i++) Scratch[i] = (byte)(v >> (8 * i));
    Buf.Write(Scratch, 0, 8);
  }
  void WStr(string s) {
    int n = Utf8.GetByteCount(s);
    if (n > Scratch.Length) Scratch = new byte[Math.Max(n, Scratch.Length * 2)];
    Utf8.GetBytes(s, 0, s.Length, Scratch, 0);
    Buf.Write(Scratch, 0, n);
  }

  string Hash(MethodDefinition m) {
    if (!m.HasBody) return "-";
    Buf.SetLength(0);
    foreach (var i in m.Body.Instructions) {
      WInt((int)i.OpCode.Code);
      if (i.Operand is MethodReference mr) {
        WStr(mr.FullName);
      } else if (i.Operand is FieldReference fr) {
        WStr(fr.FullName);
      } else if (i.Operand is string str) {
        WStr(str);
      } else if (i.Operand is int iv) {
        WInt(iv);
      } else if (i.Operand is long lv) {
        WLong(lv);
      } else if (i.Operand is float fv) {
        Buf.Write(BitConverter.GetBytes(fv), 0, 4);
      } else if (i.Operand is double dv) {
        Buf.Write(BitConverter.GetBytes(dv), 0, 8);
      } else if (i.Operand is TypeReference tr) {
        WStr(tr.FullName);
      }
    }
    return Hex16(Sha.ComputeHash(Buf.GetBuffer(), 0, (int)Buf.Length));
  }

  public Dictionary<string,string> Map(string path) {
    var d = new Dictionary<string,string>();
    var asm = AssemblyDefinition.ReadAssembly(path);
    foreach (var t in asm.MainModule.GetTypes())
      foreach (var m in t.Methods)
        d[Key(m)] = Hash(m) + "\t" + (m.HasBody ? m.Body.Instructions.Count.ToString() : "0");
    return d;
  }
}

static class AsmBodyDiff {
  static void Main(string[] args) {
    Dictionary<string,string> a = null, b = null;
    var t1 = new Thread(() => { a = new BodyHasher().Map(args[0]); });
    var t2 = new Thread(() => { b = new BodyHasher().Map(args[1]); });
    t1.Start(); t2.Start(); t1.Join(); t2.Join();
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
        print(f"# {label} {path} bytes={path.stat().st_size} sha256={tooling.sha256_file(path)}")

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
