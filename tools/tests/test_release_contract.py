#!/usr/bin/env python3
"""release-contract.md against the repository it describes.

The contract is the only in-tree record of which series a tag belongs to and
what is waiting for the next cut. Both halves go stale silently: a tag cut
without a table row, a row left behind by a deleted tag, and an Unreleased
section that keeps claiming a commit count long after the commits under it
moved. Each is checked here against git, so the drift is a gate failure
rather than something a reader has to notice.

The commit-count check applies while commits are unreleased. Right after a cut
the range is empty and the section is reset as part of the next edit, which is
not a reason to fail the tag's own CI run.

Skips with a named reason when the checkout has no git tags (a source archive,
a shallow clone with no tags), since there is no release model to compare to.

Usage: python3 tools/tests/test_release_contract.py
"""

from __future__ import annotations

import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

CONTRACT = _common.DOCS / "releases" / "release-contract.md"
# `| `v3.2.0` | 2026-09-21 | subject |` rows of the tag history table.
TAG_ROW = re.compile(r"^\|\s*`(v[0-9]+\.[0-9]+\.[0-9]+)`\s*\|")
# "**49 commits after `v3.2.0` (2026-09-21) as of 2026-09-28.**"
COUNT_CLAIM = re.compile(r"\*\*(?P<count>[0-9]+) commits? after `(?P<tag>v[0-9]+\.[0-9]+\.[0-9]+)`")
NEXT_CUT = re.compile(r"[Tt]he next cut is `(?P<version>v[0-9]+\.[0-9]+\.[0-9]+)`")


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=_common.REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    ).stdout


def unreleased_section(text: str) -> str:
    match = re.search(r"^## Unreleased$(.*?)(?=^## )", text, re.M | re.S)
    return match.group(1) if match else ""


def main() -> int:
    if not CONTRACT.is_file():
        print(f"SKIP: no release contract at {CONTRACT}")
        return 0
    try:
        tags = {t for t in git("tag", "-l").split() if t}
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"SKIP: git tags unavailable ({exc})")
        return 0
    if not tags:
        print("SKIP: checkout carries no tags; nothing to compare the contract to")
        return 0

    text = CONTRACT.read_text(encoding="utf-8")
    bad: list[str] = []

    history = re.search(r"^## Tag history$(.*?)(?=^## )", text, re.M | re.S)
    if history is None:
        bad.append("no '## Tag history' section")
    else:
        rows = {
            m.group(1) for m in (TAG_ROW.match(line) for line in history.group(1).splitlines()) if m
        }
        for tag in sorted(tags - rows):
            bad.append(f"{tag}: tagged but no row in the tag history table")
        for tag in sorted(rows - tags):
            bad.append(f"{tag}: in the tag history table but not a tag in this checkout")

    section = unreleased_section(text)
    if not section:
        bad.append("no '## Unreleased' section")
    else:
        claim = COUNT_CLAIM.search(section)
        if claim is None:
            bad.append(
                "Unreleased states no commit count; say "
                "'**N commits after `vX.Y.Z` (date)**' so the section can be checked"
            )
        else:
            base, stated = claim.group("tag"), int(claim.group("count"))
            if base not in tags:
                bad.append(f"Unreleased counts from {base}, which is not a tag in this checkout")
            else:
                actual = int(git("rev-list", "--count", f"{base}..HEAD").strip())
                if actual != stated:
                    bad.append(
                        f"Unreleased claims {stated} commits after {base}; "
                        f"there are {actual} (update the count and the entries below it)"
                    )
                elif actual > 0 and not re.search(r"^\s*[-*] ", section, re.M):
                    bad.append(f"{actual} commits are unreleased but the section lists no entries")

    for match in NEXT_CUT.finditer(text):
        version = match.group("version")
        if version in tags:
            bad.append(f"the next cut is {version}, which is already a published tag")

    if bad:
        for b in bad:
            print("FAIL:", b)
        return 1
    print(f"OK: {len(tags)} tags match the contract, and its Unreleased section matches HEAD")
    return 0


if __name__ == "__main__":
    sys.exit(main())
