#!/usr/bin/env python3
"""Every tool that publishes a file flushes it before the rename.

`tooling.publish` is the one place a staged file lands: `os.replace` alone is
atomic against a concurrent reader, so a half-written file is never visible,
but it does not flush. A crash between the rename and the write-back leaves the
destination empty or short, and the pins a gate reads have no earlier copy to
fall back on. The order the helper keeps is the property under test, along
with the failure path (a flush that fails must leave the previous contents in
place) and the fact that no tool still renames a staged file on its own.

Usage: python3 tools/tests/test_durable_publish.py
"""

from __future__ import annotations

import os
import re
import sys
import tempfile
from pathlib import Path
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common
import tooling

TOOLS = _common.TOOLS
# The helper is the one place allowed to rename a staged file.
PUBLISHER = "tooling.py"


def stage(directory: Path, text: str) -> Path:
    """Write `text` to a staged file beside the destination, closed."""
    fd, name = tempfile.mkstemp(prefix=".staged-", dir=directory)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(text)
    return Path(name)


def test_publish_lands_bytes() -> None:
    with tempfile.TemporaryDirectory(dir=_common.scratch_dir()) as td:
        dest = Path(td) / "pins.json"
        dest.write_text("old\n", encoding="utf-8")
        tmp = stage(Path(td), "new\n")
        tooling.publish(tmp, dest)
        assert not tmp.exists(), "the staged file survived the rename"
        assert dest.read_text(encoding="utf-8") == "new\n"


def test_flush_precedes_rename() -> None:
    """The data is on disk before the name points at it, and the directory
    entry is flushed after: a reader either sees the whole old file or the
    whole new one, and a crash cannot leave an empty destination behind."""
    order: list[str] = []
    real_fsync, real_replace = os.fsync, os.replace

    def spy_fsync(fd: int) -> None:
        order.append("fsync")
        real_fsync(fd)

    def spy_replace(src: Path, dst: Path) -> None:
        order.append("replace")
        real_replace(src, dst)

    with tempfile.TemporaryDirectory(dir=_common.scratch_dir()) as td:
        dest = Path(td) / "pins.json"
        dest.write_text("old\n", encoding="utf-8")
        tmp = stage(Path(td), "new\n")
        with (
            mock.patch.object(os, "fsync", spy_fsync),
            mock.patch.object(os, "replace", spy_replace),
        ):
            tooling.publish(tmp, dest)
    assert order[0] == "fsync", f"the rename ran before the flush: {order}"
    assert order[-1] == "fsync", f"the directory entry was never flushed: {order}"
    assert "replace" in order, f"the staged file was never renamed: {order}"


def test_failed_flush_keeps_previous_file() -> None:
    def boom(_fd: int) -> None:
        raise OSError(5, "I/O error")

    with tempfile.TemporaryDirectory(dir=_common.scratch_dir()) as td:
        dest = Path(td) / "pins.json"
        dest.write_text("old\n", encoding="utf-8")
        tmp = stage(Path(td), "new\n")
        with mock.patch.object(os, "fsync", boom):
            try:
                tooling.publish(tmp, dest)
            except OSError:
                pass
            else:
                raise AssertionError("a failed flush was reported as a successful publish")
        assert dest.read_text(encoding="utf-8") == "old\n", "a failed flush truncated the file"
        assert tmp.exists(), "the staged file was consumed by a failed publish"


def test_fsync_dir_tolerates_a_non_directory() -> None:
    """A host that cannot fsync a directory (Windows has no O_DIRECTORY, and a
    caller may pass a path that is not one) keeps the data flush instead of
    turning a completed rename into a failed publish."""
    with tempfile.TemporaryDirectory(dir=_common.scratch_dir()) as td:
        plain = Path(td) / "not-a-dir"
        plain.write_text("x", encoding="utf-8")
        tooling.fsync_dir(plain)
        tooling.fsync_dir(Path(td) / "missing")


def test_no_tool_renames_its_own_staged_file() -> None:
    """The helper is the only writer of that rule, so the flush cannot be
    skipped by a new tool that copies the publish idiom from an old one."""
    pattern = re.compile(r"\bos\.(?:replace|rename)\s*\(")
    offenders: list[str] = []
    for path in sorted(TOOLS.rglob("*.py")):
        if path.name == PUBLISHER:
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if pattern.search(line) and not line.lstrip().startswith("#"):
                offenders.append(f"{path.relative_to(_common.REPO)}:{number}: {line.strip()}")
    assert not offenders, "a staged file is renamed without a flush:\n" + "\n".join(offenders)


def main() -> int:
    for name, test in sorted(globals().items()):
        if name.startswith("test_") and callable(test):
            test()
            print(f"ok: {name}")
    print("OK: every tool that publishes a file flushes it before the rename")
    return 0


if __name__ == "__main__":
    sys.exit(main())
