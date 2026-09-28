#!/usr/bin/env python3
"""dump_diff.py: the drift report must name every change, and refuse a bad pair.

The tool answers "what changed between two il/full-<version>/ trees", which is
the question every TFP update is triaged with, so a silent miss is the whole
failure mode: a type that dropped out of the intersection walk, a method whose
body moved by one instruction, or an input path that is not a dump tree at all
and therefore diffs to nothing. The last one is the dangerous case, and the
tool already fails closed on it; that behavior is what keeps a wrong path from
reading as "no drift".

Synthetic dump trees, so the expectations are the dump format itself rather
than whatever a live dump happens to contain today. The fixture carries one
change of every kind the report claims to name: kind/base, interfaces, fields,
an added method, a removed method, a changed body, a body that only moved its
IL offsets, a type added on one side, and a type removed from it. Every method
body is followed by the blank line the format uses, because that line is what
ends the body: a fixture without one folds the next method's text into it.

Usage: python3 tools/tests/test_dump_diff.py
"""

from __future__ import annotations

import functools
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

TOOL = _common.TOOLS / "dump_diff.py"
run = functools.partial(_common.run_cli, TOOL)

BODY_TAIL = "\n"
OLD_A = (
    "// ==== Game.A ====\n"
    "// kind base=Object interfaces=IFoo\n"
    "// fields: Int32 a\n"
    "// Game.A::M() IL=2\n"
    "IL_0000: nop\n"
    "IL_0001: ret\n"
    "\n"
    "// Game.A::Gone() IL=1\n"
    "IL_0000: ret\n"
    "\n"
    "// Game.A::Shifted() IL=3\n"
    "IL_0000: nop\n"
    "IL_0001: nop\n"
    "IL_0002: ret\n"
    "\n"
    "// Game.A::Mut() IL=2\n"
    "IL_0000: nop\n"
    "IL_0001: ret\n"
)
NEW_A = (
    "// ==== Game.A ====\n"
    "// kind base=Other interfaces=IBar\n"
    "// fields: Int32 a, Int32 b\n"
    "// Game.A::M() IL=2\n"
    "IL_0000: nop\n"
    "IL_0001: ret\n"
    "\n"
    "// Game.A::Fresh() IL=1\n"
    "IL_0000: ret\n"
    "\n"
    "// Game.A::Shifted() IL=3\n"
    "IL_0009: nop\n"
    "IL_0010: nop\n"
    "IL_0011: ret\n"
    "\n"
    "// Game.A::Mut() IL=2\n"
    "IL_0000: nop\n"
    "IL_0001: ldc.i4.1\n"
)
UNCHANGED = "// ==== Game.Only ====\n// kind class Only\n// fields: \n"


def tree(root: Path, files: dict[str, str]) -> None:
    for relative, text in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="dump-diff-", dir=_common.scratch_dir()) as td:
        old, new = Path(td) / "old", Path(td) / "new"
        tree(old, {"Sub/A.il.txt": OLD_A, "Sub/Only.il.txt": UNCHANGED})
        tree(new, {"Sub/A.il.txt": NEW_A, "Sub/Same.il.txt": UNCHANGED})

        report = run(str(old), str(new))
        assert report.returncode == 0, report
        lines = report.stdout.splitlines()
        assert "== Sub/A.il.txt" in lines, lines
        # A type that is identical on both sides is not a drift category.
        assert "== Sub/Same.il.txt" not in lines, lines
        for want in (
            "  base/kind: base=Object -> base=Other",
            "  interfaces: IFoo -> IBar",
            "  fields: Int32 a -> Int32 a, Int32 b",
            "  +methods (1): Game.A::Fresh()",
            "  -methods (1): Game.A::Gone()",
            # The body report carries the IL count on both sides, so a reader
            # can size the change without re-running the tool.
            "  ~method Game.A::Mut() (IL 2->2)",
        ):
            assert want in lines, f"missing {want!r} in {lines}"
        # A body that only moved its IL offsets is not a method change: the
        # offsets are stripped before the comparison, so naming it would report
        # every renumbered dump as drift.
        assert "Game.A::Shifted()" not in report.stdout, report.stdout
        # A type on one side only is the largest single drift category, and the
        # intersection walk above cannot see it.
        assert "-- Sub/Only.il.txt" in lines, lines

        tree(new, {"Sub/Added.il.txt": "// ==== Game.Added ====\n// kind class Added\n"})
        with_added = run(str(old), str(new))
        assert "++ Sub/Added.il.txt" in with_added.stdout.splitlines(), with_added.stdout
        # The filter is a regex on the relative type path, and it gates the
        # one-sided markers too: a filtered-out addition is not printed.
        only_a = run(str(old), str(new), r"^Sub/A\.il\.txt$")
        assert only_a.returncode == 0, only_a
        assert "++ Sub/Added.il.txt" not in only_a.stdout, only_a.stdout
        assert "-- Sub/Only.il.txt" not in only_a.stdout, only_a.stdout
        assert "== Sub/A.il.txt" in only_a.stdout, only_a.stdout
        nothing = run(str(old), str(new), r"^does-not-exist$")
        assert nothing.returncode == 0, nothing
        assert nothing.stdout.strip() == "", nothing.stdout

        # An identical pair is the clean case the tool is trusted for: empty
        # stdout, exit 0, so `dump_diff.py a b > report` produces a report with
        # no drift in it rather than a failure.
        same = run(str(old), str(old))
        assert same.returncode == 0, same
        assert same.stdout.strip() == "", same.stdout

        # Fail closed. A path that is not a directory, and a directory holding
        # no dumps, both diff to nothing if they are accepted, and a wrong path
        # reading as "no drift" is the one answer that must never ship.
        missing = run(str(old), str(Path(td) / "nope"), str(new))
        assert missing.returncode == 2, missing
        assert "new-full-dir is not a directory" in missing.stderr, missing.stderr
        empty = Path(td) / "empty"
        empty.mkdir()
        no_dumps = run(str(old), str(empty), str(new))
        assert no_dumps.returncode == 2, no_dumps
        assert "holds no *.il.txt dumps" in no_dumps.stderr, no_dumps.stderr
        # A filter that is not a regex is a usage error, not a filter that
        # matches nothing.
        bad_re = run(str(old), str(new), "[")
        assert bad_re.returncode == 2, bad_re
        assert "not a valid regex" in bad_re.stderr, bad_re.stderr
        # The usage line is stderr, so redirecting stdout to a report never
        # writes it into the report.
        usage = run(str(old))
        assert usage.returncode == 2, usage
        assert usage.stdout == "", usage.stdout
        assert "usage:" in usage.stderr, usage.stderr
    print("OK: dump_diff names every drift category and fails closed on a bad input pair")


if __name__ == "__main__":
    main()
