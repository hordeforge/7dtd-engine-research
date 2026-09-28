#!/usr/bin/env python3
"""Method-level diff of two il/full-<version> dump sets.

Each type file (.il.txt) has:
  // ==== TypeName.FullName ====
  // kind base=... interfaces=...
  // fields: ...
  then per method:
  // TypeName::Method(param list) IL=N
  IL_xxxx: instruction
  ...
  followed by an empty line.

Compare old vs new per type:
  - header (kind/base/interfaces) changes
  - field list changes
  - added / removed / changed methods
  - per-method IL: normalized instruction diff

Usage: python3 tools/dump_diff.py <old-full-dir> <new-full-dir> [type-filter-regex]
Exit codes: 0 the pair was compared, 2 unusable input.
"""

from __future__ import annotations

import argparse
import difflib
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

METHOD_RE = re.compile(r"^// (.+) IL=(\d+)$")
HEADER_RE = re.compile(r"^// kind (.*?)(?: interfaces=(.*))?$")
FIELDS_RE = re.compile(r"^// fields: (.*)$")


@dataclass
class TypeInfo:
    name: str
    kind_line: str = ""
    interfaces: str = ""
    fields: str = ""
    methods: dict[str, list[str]] = field(default_factory=dict)
    method_sigs: dict[str, str] = field(default_factory=dict)  # sig -> IL count

    @property
    def method_names(self) -> list[str]:
        return sorted(self.methods)


def parse_type(path: Path) -> TypeInfo:
    info = TypeInfo(name=path.stem)
    cur: list[str] | None = None
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if line.startswith("// kind"):
                m = HEADER_RE.match(line)
                if m:
                    info.kind_line = m.group(1)
                    info.interfaces = m.group(2) or ""
            elif line.startswith("// fields:"):
                m = FIELDS_RE.match(line)
                if m:
                    info.fields = m.group(1)
            elif line.startswith("// "):
                m = METHOD_RE.match(line)
                if m:
                    sig = m.group(1)
                    info.method_sigs[sig] = m.group(2)
                    cur = []
                    info.methods[sig] = cur
                else:
                    cur = None
            elif cur is not None:
                cur.append(line)
    return info


def strip_offsets(il_lines: list[str]) -> list[str]:
    out = []
    for line in il_lines:
        if line.startswith("IL_"):
            out.append(line.split(": ", 1)[-1])
        else:
            out.append(line)
    return out


def method_diff(old: list[str], new: list[str]) -> tuple[bool, list[str]]:
    o = strip_offsets(old)
    n = strip_offsets(new)
    if o == n:
        return False, []
    sm = difflib.SequenceMatcher(a=o, b=n, autojunk=False)
    out: list[str] = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        for line in o[i1:i2]:
            out.append("- " + line)
        for line in n[j1:j2]:
            out.append("+ " + line)
    return True, out


def diff_type(old: TypeInfo, new: TypeInfo, full: bool = False) -> list[str]:
    out: list[str] = []
    if old.kind_line != new.kind_line:
        out.append(f"  base/kind: {old.kind_line} -> {new.kind_line}")
    if old.interfaces != new.interfaces:
        out.append(f"  interfaces: {old.interfaces} -> {new.interfaces}")
    if old.fields != new.fields:
        out.append(f"  fields: {old.fields} -> {new.fields}")
    added = sorted(set(new.methods) - set(old.methods))
    removed = sorted(set(old.methods) - set(new.methods))
    if added:
        out.append(f"  +methods ({len(added)}): " + ", ".join(added))
    if removed:
        out.append(f"  -methods ({len(removed)}): " + ", ".join(removed))
    for sig in sorted(set(old.methods) & set(new.methods)):
        if old.methods[sig] == new.methods[sig]:
            continue
        changed_body, lines = method_diff(old.methods[sig], new.methods[sig])
        if not changed_body:
            # Same body once the IL offsets are stripped, so the only
            # difference is where the dumper numbered the instructions.
            # The extra "and the IL marker differs" clause this used to carry
            # defeated strip_offsets: a recompile renumbers the offsets and
            # keeps the marker, so every method in the tree was reported as
            # changed and the real drift was buried.
            continue
        out.append(
            f"  ~method {sig} (IL {old.method_sigs.get(sig, '?')}->{new.method_sigs.get(sig, '?')})"
        )
        if full:
            out.extend("    " + x for x in lines)
    return out


OLD_METAVAR = "old-full-dir"
NEW_METAVAR = "new-full-dir"


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description="Method-level diff of two il/full-<version> dump trees.",
        epilog="exit 0 = the pair was compared, 2 = unusable input",
    )
    ap.add_argument(
        "old_dir", metavar=OLD_METAVAR, help="older dump tree (the il/full-<version> directory)"
    )
    ap.add_argument("new_dir", metavar=NEW_METAVAR, help="newer dump tree to compare against")
    ap.add_argument(
        "type_filter",
        nargs="?",
        default=None,
        metavar="type-filter-regex",
        help="regex on the relative type path, e.g. '^Sub/A' (default: every type)",
    )
    return ap


def main(argv: list[str] | None = None) -> int:
    # argparse answers --help on stdout (exit 0) and a bad invocation on stderr
    # (exit 2), so `dump_diff.py a b > report` never lands usage text in the
    # report; stdout stays the diff and nothing else.
    args = build_parser().parse_args(argv)
    old_dir = Path(args.old_dir)
    new_dir = Path(args.new_dir)
    try:
        flt = re.compile(args.type_filter if args.type_filter is not None else ".*")
    except re.error as exc:
        print(f"dump_diff: type-filter-regex is not a valid regex: {exc}", file=sys.stderr)
        return 2

    for label, directory in ((OLD_METAVAR, old_dir), (NEW_METAVAR, new_dir)):
        if not directory.is_dir():
            # A wrong path makes rglob() yield nothing, which reads as "no
            # drift" and exits 0. Name the argument instead.
            print(f"dump_diff: {label} is not a directory: {directory}", file=sys.stderr)
            return 2
    old_files = {p.relative_to(old_dir): p for p in old_dir.rglob("*.il.txt")}
    new_files = {p.relative_to(new_dir): p for p in new_dir.rglob("*.il.txt")}

    for label, files in (("old-full-dir", old_files), ("new-full-dir", new_files)):
        if not files:
            # Same silence as a wrong path, reached by a dump run that
            # aborted or wrote elsewhere.
            print(
                f"dump_diff: {label} holds no *.il.txt dumps: "
                f"{old_dir if label == 'old-full-dir' else new_dir}",
                file=sys.stderr,
            )
            return 2

    # common files
    for rel in sorted(set(old_files) & set(new_files)):
        if not flt.search(str(rel)):
            continue
        o = parse_type(old_files[rel])
        n = parse_type(new_files[rel])
        d = diff_type(o, n, full=False)
        if d:
            print(f"== {rel}")
            for x in d:
                print(x)

    # A type present on one side only is the largest single drift category,
    # and the intersection-only walk above could not report it.
    for rel in sorted(set(new_files) - set(old_files)):
        if flt.search(str(rel)):
            print(f"++ {rel}")
    for rel in sorted(set(old_files) - set(new_files)):
        if flt.search(str(rel)):
            print(f"-- {rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
