#!/usr/bin/env python3
"""release.sh: the dry-run contract and the refusals, without touching git.

The release script is the one tool that publishes; its checks are what keep a
release honest, so they are pinned here. Every case runs with `--dry-run` or
fails before any write, and the test asserts afterwards that no tag appeared.

Usage: python3 tools/tests/test_release_script.py
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

RELEASE = _common.TOOLS / "release.sh"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([str(RELEASE), *args], text=True, capture_output=True, check=False)


def tag_exists(name: str) -> bool:
    return (
        subprocess.run(
            ["git", "rev-parse", "-q", "--verify", f"refs/tags/{name}"],
            cwd=_common.REPO,
            capture_output=True,
        ).returncode
        == 0
    )


def main() -> None:
    help_run = run("--help")
    assert help_run.returncode == 0, help_run
    assert "--dry-run" in help_run.stdout, help_run.stdout

    assert run().returncode == 2
    assert run("1.2.3").returncode == 2
    assert "version must look like" in run("1.2.3").stderr
    assert run("v9.9.9", "--notes", "/nope/notes.md", "--dry-run").returncode == 2
    assert run("v9.9.9", "--bad-flag").returncode == 2

    with tempfile.TemporaryDirectory(prefix="release_", dir=_common.scratch_dir()) as tmp:
        notes = Path(tmp) / "notes.md"
        notes.write_text("fixture notes\n", encoding="utf-8")

        # --dry-run skips the dirty-tree check, so an existing tag is reached on
        # any worktree state (a test must not depend on the checkout being clean).
        existing = run("v3.2.0", "--notes", str(notes), "--dry-run")
        assert existing.returncode == 2, existing.stdout
        assert "already exists" in existing.stderr, existing.stderr

        dry = run("v9.9.9", "--notes", str(notes), "--dry-run")
        assert dry.returncode == 0, (dry.stdout, dry.stderr)
        for step in ("git tag -a v9.9.9", "gh release create v9.9.9", "dry run, nothing changed"):
            assert step in dry.stdout, (step, dry.stdout)
        assert not tag_exists("v9.9.9"), "a dry run created a tag"

    print("OK: release.sh refuses bad input and existing tags, and its dry run writes nothing")


if __name__ == "__main__":
    main()
