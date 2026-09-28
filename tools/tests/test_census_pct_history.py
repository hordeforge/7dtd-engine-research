#!/usr/bin/env python3
"""census-pct.py: recording a census row twice must equal recording it once.

The history file is a committed artifact under workspace/outputs/, and `make
census` can run more than once: a retried CI step, a re-measure of the same
build, or two runs at the same time. The file is keyed on the date column, so a
repeat replaces its own row rather than adding a duplicate, the header is
written exactly once, and concurrent runs neither lose a row nor leave a
truncated CSV behind.

Usage: python3 tools/tests/test_census_pct_history.py
"""

from __future__ import annotations

import multiprocessing
import os
import sys
import tempfile
import unicodedata
from pathlib import Path
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

TOOL = _common.TOOLS / "census-pct.py"
HISTORY = _common.REPO / "workspace" / "outputs" / "census-history.csv"
HEADER = "date,game_types,narrated,catalogued,classified,unaccounted,narrated_pct\n"
ROW = "2026-01-01,3681,3681,0,0,0,100.0%\n"
WRITERS = 8
ROWS_PER_WRITER = 25


def load_module() -> Any:
    return _common.load_module(TOOL, "census_pct")


def writer(path: str, index: int) -> None:
    """Child-process body: the exact call main() makes on --history.

    The row key is the first column (a UTC date in real use); the synthetic
    values here give every concurrent row a distinct key, so each run must
    survive rather than replace a sibling.
    """
    module = load_module()
    for row in range(ROWS_PER_WRITER):
        key = "2026-01-01-run%d-%02d" % (index, row)
        module.record_history(path, HEADER, f"{key},{index},{row},0,0,0,0.0%\n")


def main() -> None:
    rows = HISTORY.read_text(encoding="utf-8").splitlines(keepends=True)
    assert rows, f"{HISTORY}: empty"
    assert rows[0] == HEADER, f"{HISTORY}: first line is not the header"
    dupes = sum(1 for line in rows if line == HEADER)
    assert dupes == 1, f"{HISTORY}: {dupes} header lines (a racing run truncated it)"
    dates = [line.split(",", 1)[0] for line in rows[1:]]
    repeated = sorted({date for date in dates if dates.count(date) > 1})
    assert not repeated, (
        f"{HISTORY}: repeated dates {repeated} (a rerun appended instead of replacing)"
    )

    with tempfile.TemporaryDirectory(dir=_common.scratch_dir()) as td:
        fresh = os.path.join(td, "census-history.csv")
        module = load_module()

        assert module.record_history(fresh, HEADER, ROW) == "appended"
        once = Path(fresh).read_text(encoding="utf-8")
        assert once == HEADER + ROW, "a fresh history file is not header + one row"

        # The property under test: the same run again changes nothing.
        assert module.record_history(fresh, HEADER, ROW) == "unchanged"
        assert Path(fresh).read_text(encoding="utf-8") == once, "a rerun rewrote an identical row"
        module.record_history(fresh, HEADER, ROW)
        module.record_history(fresh, HEADER, ROW)
        assert Path(fresh).read_text(encoding="utf-8") == once, "repeated runs grew the file"

        # A same-date re-measure with different numbers replaces, never appends.
        assert (
            module.record_history(fresh, HEADER, "2026-01-01,3700,3690,0,0,10,99.7%\n")
            == "replaced"
        )
        lines = Path(fresh).read_text(encoding="utf-8").splitlines()
        assert lines == [HEADER.rstrip("\n"), "2026-01-01,3700,3690,0,0,10,99.7%"], lines

        # A different date accumulates, and re-recording an earlier date leaves
        # the later rows in place.
        module.record_history(fresh, HEADER, "2026-01-02,3700,3690,0,0,10,99.7%\n")
        module.record_history(fresh, HEADER, "2026-01-01,3681,3681,0,0,0,100.0%\n")
        lines = Path(fresh).read_text(encoding="utf-8").splitlines()
        assert lines == [
            HEADER.rstrip("\n"),
            ROW.rstrip("\n"),
            "2026-01-02,3700,3690,0,0,10,99.7%",
        ], lines

        # A missing header is restored, not duplicated.
        Path(fresh).write_text(ROW, encoding="utf-8")
        module.record_history(fresh, HEADER, "2026-01-03,1,1,0,0,0,100.0%\n")
        lines = Path(fresh).read_text(encoding="utf-8").splitlines()
        assert lines.count(HEADER.rstrip("\n")) == 1, lines
        assert len(lines) == 3, lines

        # A file whose first line is a different width is not a lost header: it
        # is another schema's CSV, and writing a row would carry that line as
        # data under columns it does not have.
        foreign = os.path.join(td, "foreign.csv")
        Path(foreign).write_text("date,game_types,narrated\n2026-01-01,1,1\n", encoding="utf-8")
        refused = "a foreign-width history file was written to"
        try:
            module.record_history(foreign, HEADER, "2026-01-04,1,1,0,0,0,100.0%\n")
        except ValueError as exc:
            refused = (
                "the refusal does not name the column mismatch"
                if ("different column set" not in str(exc))
                else ""
            )
        assert not refused, refused
        assert Path(foreign).read_text(encoding="utf-8") == (
            "date,game_types,narrated\n2026-01-01,1,1\n"
        ), "the refused run still modified the file"

        # A history file whose name is not valid UTF-8 is legal on the host the
        # tool runs on (Linux stores raw bytes), and --history takes the name
        # from the command line. Hashing it strictly raised UnicodeEncodeError
        # before the row was written; the lock must be derivable either way, and
        # the same bytes must keep mapping to the same lock.
        raw = os.path.join(os.fsencode(td), b"census-\xff.csv")
        weird = os.fsdecode(raw)
        assert "\udcff" in weird, "fixture path must carry an undecodable byte"
        assert module.history_lock(weird) == module.history_lock(weird)
        assert module.history_lock(weird) != module.history_lock(fresh)

        # A decomposed and a composed spelling of the same name are the same
        # file, so the lock must not be a second writer's lock.
        composed = os.path.join(td, "café-history.csv")
        decomposed = os.path.join(td, unicodedata.normalize("NFD", "café-history.csv"))
        assert composed != decomposed
        assert module.history_lock(composed) == module.history_lock(decomposed)

        concurrent = os.path.join(td, "concurrent.csv")
        ctx = multiprocessing.get_context("fork")
        procs = [ctx.Process(target=writer, args=(concurrent, i)) for i in range(WRITERS)]
        for proc in procs:
            proc.start()
        try:
            for proc in procs:
                proc.join(120)
                assert proc.exitcode == 0, f"recorder exited {proc.exitcode}"
        finally:
            # A writer that wedges on the flock, or an assert that fires first,
            # must not leave eight live children holding the scratch tree.
            for proc in procs:
                if proc.is_alive():
                    proc.kill()
                proc.join()
        lines = Path(concurrent).read_text(encoding="utf-8").splitlines()
        assert lines[0] == HEADER.rstrip("\n"), "header is not the first line"
        assert lines.count(HEADER.rstrip("\n")) == 1, f"{len(lines)} lines, header appears twice"
        expected = WRITERS * ROWS_PER_WRITER
        assert len(lines) - 1 == expected, f"{len(lines) - 1} rows recorded, expected {expected}"
        assert len(set(lines[1:])) == expected, "a concurrent run lost a row"
    print(f"OK: a repeated census run rewrites nothing; {WRITERS} concurrent runs keep every row")


if __name__ == "__main__":
    main()
