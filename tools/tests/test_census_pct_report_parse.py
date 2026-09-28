#!/usr/bin/env python3
"""census-pct.py: a measurement it could not take must not read as a measurement.

Two silent zero paths used to hide a broken census run. A coverage report that
could not be read returned 0 reached types, and the caller prints the
"reached in the server call graph" line only for a non-zero count, so a
permission error or a truncated report dropped the row from a report whose
other rows still looked complete, and `make census` recorded a history row
anyway. Census.exe output missing its two whole-assembly rows defaulted to 0,
which reads as a smaller assembly.

Both now signal instead: the report parse returns None and names the file on
stderr, and the census key check raises with the keys it did and did not see.

Usage: python3 tools/tests/test_census_pct_report_parse.py
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import os
import sys
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

TOOL = _common.TOOLS / "census-pct.py"
REPORT_ROW = "| Reached types (incl. compiler-generated) | 4211 |\n"


def load_module() -> Any:
    spec = importlib.util.spec_from_file_location("census_pct_parse", TOOL)
    assert spec is not None, TOOL
    assert spec.loader is not None, TOOL
    module: Any = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    module = load_module()
    tmp = _common.scratch_dir() / "census-pct-report-parse"
    tmp.mkdir(parents=True, exist_ok=True)

    report = tmp / "coverage.md"
    report.write_text(f"# Coverage\n\n{REPORT_ROW}", encoding="utf-8")
    assert module.parse_report_reached_types(str(report)) == 4211

    # A report with no such row and an unreadable report are both "not
    # measured". Neither may answer with a number.
    empty = tmp / "empty.md"
    empty.write_text("# Coverage\n\nno rows here\n", encoding="utf-8")
    for label, path in (("no such row", str(empty)), ("unreadable", str(tmp / "absent.md"))):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            got = module.parse_report_reached_types(path)
        assert got is None, f"{label}: returned {got!r} instead of None"
        if label == "unreadable":
            assert path in err.getvalue(), (
                f"unreadable report not named on stderr: {err.getvalue()!r}"
            )

    cen = module.parse_census("AllTypes (incl nested) = 7451\nAllMethodsWithBody = 91000\n")
    assert module.whole_assembly_counts(cen) == (7451, 91000)

    # Census.exe exits 0 either way, so only the rows tell a changed format
    # from an empty assembly.
    for stdout, missing_key in (
        ("SomeOtherCount = 3\n", "AllTypes (incl nested)"),
        ("AllTypes (incl nested) = 7451\n", "AllMethodsWithBody"),
        ("", "AllTypes (incl nested)"),
    ):
        try:
            module.whole_assembly_counts(module.parse_census(stdout))
        except ValueError as exc:
            message = str(exc)
        else:
            raise AssertionError(f"accepted census output without {missing_key!r}: {stdout!r}")
        assert missing_key in message, message

    print("OK: an unreadable coverage report and an unparseable census answer as failures")


if __name__ == "__main__":
    main()
