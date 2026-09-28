#!/usr/bin/env python3
"""Every artifact stamp goes through `tooling.generation_stamp()`.

The committed build-diff report, the census history row and the studied-build
pin each carry a UTC stamp. Read straight off the wall clock they made a run
unreplayable: the same DLL pair produced different bytes every time, and the
report's default filename carried the day it was written, so a re-run left a
second copy behind. `SOURCE_DATE_EPOCH` pins the stamp, which is what makes a
run reproducible byte-for-byte.

Two things are pinned here, DLL-free and network-free:

  1. The contract of the helper: `SOURCE_DATE_EPOCH` overrides the wall clock,
     an unset variable still yields a well-formed UTC stamp, and a value that
     is not an integer raises instead of falling back (a silently-wrong stamp
     would be written into a committed file and look recorded).
  2. That no tool reads the clock for a stamp itself. A new artifact that
     calls `datetime.now()` directly is a run that cannot be replayed, and the
     detector is self-tested so a silent no-match cannot read as a pass. The
     same rule covers `tools/src/*.cs`, whose `extracted_utc` line lands in the
     committed `tools/data/stock_facts.json`: the Mono extractor must read the
     clock only inside a method that honors `SOURCE_DATE_EPOCH`.

Usage: python3 tools/tests/test_generation_stamp.py
"""

from __future__ import annotations

import ast
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common
import tooling

STAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
PINNED_EPOCH = 1789206360  # 2026-09-12T09:46:00Z
PINNED_STAMP = "2026-09-12T09:46:00Z"
WALL_CLOCK_SKEW_S = 120
SEAM = "tooling.py"
CLOCK_CALLS = ("now", "utcnow", "today")
# tools/src/*.cs stamps a committed artifact (stock_facts.json) the same way;
# the seam there is the SOURCE_DATE_EPOCH variable, and Mono's DateTimeOffset
# is the only clock source the sources may read.
CS_CLOCK_RE = re.compile(r"DateTime(?:Offset)?\.(?:UtcNow|Now|Today)\b")
CS_SEAM = "StampEnv"
CS_STAMP_METHOD = "ExtractedStamp"
CS_METHOD_RE = re.compile(r"^  (?:static|public|private|internal)?[^;{]*\([^;]*\)[ ]*\{")


def direct_clock_reads(path: Path) -> list[tuple[str, int]]:
    """Every `datetime` clock read in a file, as (callee, line)."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    hits: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name) and func.id in CLOCK_CALLS:
            # `from datetime import now`
            hits.append((func.id, node.lineno))
        elif isinstance(func, ast.Attribute) and func.attr in CLOCK_CALLS:
            # `datetime.now(...)` or `dt.datetime.now(...)`
            root = func.value
            if (isinstance(root, ast.Name) and root.id == "datetime") or (
                isinstance(root, ast.Attribute) and root.attr == "datetime"
            ):
                hits.append((func.attr, node.lineno))
    return hits


def stamp_with(value: str | None) -> str:
    """The stamp the helper yields for `SOURCE_DATE_EPOCH` set to `value`.

    The helper reads the process environment on every call, so the variable is
    swapped in place and restored; `value` of None means unset.
    """
    previous = os.environ.pop(tooling.STAMP_ENV, None)
    if value is not None:
        os.environ[tooling.STAMP_ENV] = value
    try:
        return tooling.generation_stamp()
    finally:
        if previous is None:
            os.environ.pop(tooling.STAMP_ENV, None)
        else:
            os.environ[tooling.STAMP_ENV] = previous


def cs_method_at(lines: list[str], index: int) -> str:
    """The C# method body containing `lines[index]`.

    The sources indent members two spaces and close them at that indent, so a
    method runs from its `  ...(...) {` header to the next line that is exactly
    `  }`.
    """
    start = index
    while start >= 0 and not CS_METHOD_RE.match(lines[start]):
        start -= 1
    if start < 0:
        return ""
    end = start
    while end < len(lines) and lines[end] != "  }":
        end += 1
    return "\n".join(lines[start:end])


def cs_stamp_helpers() -> list[str]:
    """Paths of the C# stamp helpers, used as the detector's liveness proof."""
    return [
        str(path.relative_to(_common.TOOLS))
        for path in sorted(_common.TOOLS.rglob("src/*.cs"))
        if CS_STAMP_METHOD in path.read_text(encoding="utf-8")
    ]


def check_cs_sources() -> list[str]:
    """Every C# clock read must sit in a method that honors the pinned epoch."""
    failures: list[str] = []
    for path in sorted(_common.TOOLS.rglob("src/*.cs")):
        lines = path.read_text(encoding="utf-8").splitlines()
        for index, line in enumerate(lines):
            if not CS_CLOCK_RE.search(line):
                continue
            body = cs_method_at(lines, index)
            if CS_SEAM not in body:
                failures.append(
                    f"{path.relative_to(_common.TOOLS)}:{index + 1} reads the wall clock "
                    f"outside a {CS_SEAM} check: {line.strip()}"
                )
    return failures


CS_LIVENESS_SNIPPET = """class T {
  static string Stamp() {
    return DateTime.UtcNow.ToString("o");
  }
  static void Other() {
    var t = DateTime.Now;
  }
}
"""


def cs_detector_alive() -> bool:
    """The C# detector must flag a bare wall-clock read, or it reads as a pass."""
    lines = CS_LIVENESS_SNIPPET.splitlines()
    flagged = 0
    for index, line in enumerate(lines):
        if CS_CLOCK_RE.search(line) and CS_SEAM not in cs_method_at(lines, index):
            flagged += 1
    return flagged == 2


def main() -> int:
    failures: list[str] = []

    if stamp_with(str(PINNED_EPOCH)) != PINNED_STAMP:
        failures.append(f"{tooling.STAMP_ENV}={PINNED_EPOCH} did not yield {PINNED_STAMP}")
    # Surrounding whitespace is a shell habit, not a malformed epoch.
    if stamp_with(f"  {PINNED_EPOCH}\n") != PINNED_STAMP:
        failures.append(f"a padded {tooling.STAMP_ENV} was not accepted")

    wall = stamp_with(None)
    if not STAMP_RE.match(wall):
        failures.append(f"an unset {tooling.STAMP_ENV} gave {wall!r}")
    else:
        stamped = datetime.strptime(wall, tooling.STAMP_FORMAT).replace(tzinfo=timezone.utc)
        skew = abs((datetime.now(timezone.utc) - stamped).total_seconds())
        if skew > WALL_CLOCK_SKEW_S:
            failures.append(f"the fallback stamp is {skew:.0f}s away from the wall clock")

    for bad in ("bogus", "", "17.5", "1789206360x"):
        try:
            yielded = stamp_with(bad)
        except tooling.StampError:
            continue
        failures.append(f"{tooling.STAMP_ENV}={bad!r} yielded {yielded!r} instead of raising")

    # Detector liveness: the seam reads the clock, every other tool must not.
    if not direct_clock_reads(_common.TOOLS / SEAM):
        failures.append(f"detector is dead: {SEAM} no longer reads the clock")
    for path in sorted(_common.TOOLS.rglob("*.py")):
        if "tests" in path.parts or path.name == SEAM:
            continue
        for callee, line in direct_clock_reads(path):
            failures.append(
                f"{path.relative_to(_common.TOOLS)}:{line} reads the clock directly "
                f"({callee}); stamp artifacts through tooling.generation_stamp()"
            )

    helpers = cs_stamp_helpers()
    if not helpers:
        failures.append(f"detector is dead: no tools/src/*.cs defines {CS_STAMP_METHOD}")
    if not cs_detector_alive():
        failures.append(
            "detector is dead: the C# wall-clock read is not flagged on a known-bad sample"
        )
    failures.extend(check_cs_sources())

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    print("OK: artifact stamps go through generation_stamp() and replay from SOURCE_DATE_EPOCH")
    return 0


if __name__ == "__main__":
    sys.exit(main())
