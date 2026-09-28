#!/usr/bin/env python3
"""census-pct.py: the census history CSV must survive concurrent runs.

The history file is a committed artifact under workspace/outputs/, and `make
census` can run more than once at a time. Concurrent appenders must produce one
header line and one row per append; a second header mid-file, or a lost row, is
corruption of a tracked file that no gate would otherwise notice.

Usage: python3 tools/tests/test_census_pct_history.py
"""

from __future__ import annotations

import importlib.util
import multiprocessing
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

TOOL = _common.TOOLS / "census-pct.py"
HISTORY = _common.REPO / "workspace" / "outputs" / "census-history.csv"
HEADER = "date,game_types,narrated,catalogued,classified,unaccounted,narrated_pct\n"
WRITERS = 8
ROWS_PER_WRITER = 25


def load_module() -> Any:
    spec = importlib.util.spec_from_file_location("census_pct", TOOL)
    assert spec is not None, TOOL
    assert spec.loader is not None, TOOL
    module: Any = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def writer(path: str, index: int) -> None:
    """Child-process body: the exact call main() makes on --history."""
    module = load_module()
    for row in range(ROWS_PER_WRITER):
        module.append_history(path, HEADER, f"2026-01-01,run{index},{row},0,0,0,0.0%\n")


def main() -> None:
    rows = HISTORY.read_text(encoding="utf-8").splitlines(keepends=True)
    assert rows, f"{HISTORY}: empty"
    assert rows[0] == HEADER, f"{HISTORY}: first line is not the header"
    dupes = sum(1 for line in rows if line == HEADER)
    assert dupes == 1, f"{HISTORY}: {dupes} header lines (a racing run truncated it)"

    with tempfile.TemporaryDirectory(dir=_common.scratch_dir()) as td:
        fresh = os.path.join(td, "census-history.csv")
        ctx = multiprocessing.get_context("fork")
        procs = [ctx.Process(target=writer, args=(fresh, i)) for i in range(WRITERS)]
        for proc in procs:
            proc.start()
        for proc in procs:
            proc.join(120)
            assert proc.exitcode == 0, f"appender exited {proc.exitcode}"
        lines = Path(fresh).read_text(encoding="utf-8").splitlines()
        assert lines[0] == HEADER.rstrip("\n"), "header is not the first line"
        assert lines.count(HEADER.rstrip("\n")) == 1, f"{len(lines)} lines, header appears twice"
        expected = WRITERS * ROWS_PER_WRITER
        assert len(lines) - 1 == expected, f"{len(lines) - 1} rows appended, expected {expected}"
        assert len(set(lines[1:])) == expected, "a concurrent append lost a row"
    print(f"OK: {WRITERS} concurrent census runs keep one header and every row")


if __name__ == "__main__":
    main()
