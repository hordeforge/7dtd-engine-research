#!/usr/bin/env python3
"""The release-contract gate's detectors, each proved on a throwaway repo.

A gate that decides whether a release record is honest is worth as much as its
detectors actually fire: a rule written and never exercised reads green while
it checks nothing, and a rule that fires on the wrong input makes the record
unmaintainable, because the next cut stops at it. The real checkout is never
written or consulted for versions: the gate takes `--contract` and `--repo`, so
every case here runs in a sandbox with its own tags and commits.

Usage: python3 tools/tests/test_release_contract_gate.py
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

GATE = _common.TOOLS / "tests" / "test_release_contract.py"

CONTRACT = """# Contract

{history}{unreleased_section}## Cutting a release

The next cut is `{next_cut}` (tooling).
"""

HISTORY = """## Tag history

| Tag | Date | Tagged commit |
|---|---|---|
"""


def git(*args: str, cwd: Path) -> None:
    _common.run_cmd(["git", *args], cwd=cwd, check=True, capture_output=True)


def sandbox(tmp: Path, *, tag: str = "v0.4.0") -> Path:
    """A repo with one commit and, unless asked otherwise, one tag on it."""
    repo = tmp / "repo"
    repo.mkdir(parents=True)
    git("init", "-q", "-b", "main", ".", cwd=repo)
    git("config", "user.email", "test@example.invalid", cwd=repo)
    git("config", "user.name", "test", cwd=repo)
    git("commit", "-q", "--allow-empty", "-m", "init", cwd=repo)
    if tag:
        git("tag", tag, cwd=repo)
    return repo


def check(
    repo: Path,
    contract: Path,
    *,
    rows: str,
    unreleased: str,
    next_cut: str = "v0.5.0",
    history: bool = True,
    unreleased_header: bool = True,
) -> str:
    contract.write_text(
        CONTRACT.format(
            history=HISTORY + rows if history else "",
            unreleased_section="## Unreleased\n\n" + unreleased if unreleased_header else "",
            next_cut=next_cut,
        ),
        encoding="utf-8",
    )
    done = _common.run_cmd(
        [sys.executable, str(GATE), "--contract", str(contract), "--repo", str(repo)],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    assert done.returncode in (0, 1), done.stderr
    return done.stdout


def expect(repo: Path, contract: Path, wanted: str, **kwargs: object) -> str:
    out = check(repo, contract, **kwargs)  # type: ignore[arg-type]
    assert wanted in out, f"expected {wanted!r} in:\n{out}"
    return out


def main() -> int:
    row = "| `v0.4.0` | 2026-09-28 | subject |\n"
    claim = "**{n} commits after `v0.4.0` (2026-09-28) as of 2026-09-28.**\n"
    listed = claim.format(n=1) + "\n- one fix\n"

    with tempfile.TemporaryDirectory(prefix="contract-gate-", dir=_common.scratch_dir()) as td:
        tmp = Path(td)
        contract = tmp / "release-contract.md"

        # Straight after a cut: HEAD is the tag and the section still describes
        # what was released, to be reset by the next edit. Failing here is what
        # would turn a released tag's own CI run red.
        cut = sandbox(tmp / "cut")
        out = expect(cut, contract, "not counted", rows=row, unreleased=claim.format(n=3))
        assert "FAIL" not in out, out

        # One commit above the tag, described with an entry: green.
        one = sandbox(tmp / "one")
        git("commit", "-q", "--allow-empty", "-m", "later", cwd=one)
        expect(one, contract, "matches HEAD", rows=row, unreleased=listed)

        # A count that no longer matches the commits below the tag: the drift
        # the gate exists for, and the shape it must not miss.
        out = expect(one, contract, "claims 5 commits", rows=row, unreleased=claim.format(n=5))
        assert "FAIL" in out, out
        out = expect(one, contract, "lists no entries", rows=row, unreleased=claim.format(n=1))
        assert "FAIL" in out, out
        expect(one, contract, "states no commit count", rows=row, unreleased="nothing yet\n")
        expect(
            one,
            contract,
            "not a tag in this checkout",
            rows=row,
            unreleased="**2 commits after `v9.9.9` (2026-09-28) as of 2026-09-28.**\n- x\n",
        )
        expect(
            one,
            contract,
            "no '## Unreleased' section",
            rows=row,
            unreleased="",
            unreleased_header=False,
        )

        # A tag cut without a table row, a row left behind by a deleted tag, and
        # a table that is not there at all.
        expect(one, contract, "tagged but no row", rows="", unreleased=listed)
        expect(
            one,
            contract,
            "but not a tag in this checkout",
            rows=row + "| `v0.3.0` | 2026-09-22 | gone |\n",
            unreleased=listed,
        )
        expect(
            one, contract, "no '## Tag history' section", rows="", unreleased=listed, history=False
        )

        # A next cut naming a version that is already published.
        expect(
            one, contract, "already a published tag", rows=row, unreleased=listed, next_cut="v0.4.0"
        )

        # A checkout with no tags has no release model to check, so the gate
        # says so and passes rather than failing the suite.
        bare = sandbox(tmp / "bare", tag="")
        expect(bare, contract, "carries no tags", rows=row, unreleased=claim.format(n=0))

        # A missing contract is a skip naming the path, not a traceback.
        done = _common.run_cmd(
            [sys.executable, str(GATE), "--contract", str(tmp / "absent.md"), "--repo", str(one)],
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )
        assert done.returncode == 0, done.stdout
        assert "no release contract" in done.stdout, done.stdout

    print(
        "OK: the contract gate counts unreleased commits, skips the post-cut "
        "section, and catches tag rows, counts and next-cut names that drift"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
