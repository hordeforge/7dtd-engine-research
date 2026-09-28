#!/usr/bin/env python3
"""Every maintained Python CLI provides dependency-free help, is documented, and
answers a bad invocation the same way.

The tool list is discovered from the AST (`_common.argparse_clis`), not kept by
hand: a new CLI is covered the moment it exists, which is how `facts.py` and the
link/pin helpers were found absent from the old hand-kept list. Each discovered
script must print help for `--help` without importing its optional runtime
dependencies, and must be named in `tools/README.md`.

An unknown flag is the one invocation every CLI shares, so it is probed the same
way everywhere: exit 2 (a usage error, distinct from the 1 a failed check
returns) with the usage line and the offending flag on stderr, never on stdout,
so `tool --help > page` and a piped report stay clean.

A flag that parses is not enough: a value the tool cannot act on must be refused
with the same exit 2, never answered as a successful empty run. `--repo` on both
link gates and `mention_depth.py`'s positional `docs_dir` are the fixtures, each
with the negative case that used to answer "OK: 0 ... resolve" / an all-zero
table and exit 0.

Usage: python3 tools/tests/test_python_cli_usage.py
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

README = _common.TOOLS / "README.md"
UNKNOWN_FLAG = "--zzz-not-a-flag"
# (tool, argv that parses but names something the tool cannot act on).
BAD_VALUES = (
    ("cross_repo_links.py", ("--repo", "not-a-sibling-repo")),
    ("zdtd_cite_check.py", ("--repo", "not-a-sibling-repo")),
    ("mention_depth.py", ("/nonexistent-docs-dir",)),
    ("steam/steam_builds.py", ("--pins", "/nonexistent-pins.json")),
)


def run(script: Path, *argv: str) -> subprocess.CompletedProcess[str]:
    return _common.run_cmd(
        [sys.executable, str(script), *argv],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )


def main() -> None:
    readme = README.read_text(encoding="utf-8")
    scripts = _common.argparse_clis()
    # Detector liveness: discovery must see real tools and must not walk tests/.
    assert scripts, "no Python CLI discovered under tools/"
    assert _common.TOOLS / "research_diff.py" in scripts, [str(p) for p in scripts]
    assert not [p for p in scripts if "tests" in p.parts], scripts
    broken: list[str] = []
    undocumented: list[str] = []
    for path in scripts:
        relative = str(path.relative_to(_common.TOOLS))
        result = run(path, "--help")
        if result.returncode != 0 or "usage:" not in result.stdout.lower():
            broken.append(
                f"{relative}: rc={result.returncode}, stderr={result.stderr.strip()[:160]!r}"
            )
        result = run(path, UNKNOWN_FLAG)
        if result.returncode != 2 or "usage:" not in result.stderr.lower():
            broken.append(
                f"{relative} {UNKNOWN_FLAG}: rc={result.returncode}, "
                f"stderr={result.stderr.strip()[:160]!r}"
            )
        elif result.stdout.strip():
            broken.append(f"{relative} {UNKNOWN_FLAG}: usage leaked onto stdout")
        if path.name not in readme:
            undocumented.append(relative)
    assert not broken, "\n".join(broken)
    assert not undocumented, "CLIs missing from tools/README.md: " + ", ".join(undocumented)
    unusable: list[str] = []
    for name, argv in BAD_VALUES:
        script = _common.TOOLS / name
        result = run(script, *argv)
        if result.returncode != 2 or not result.stderr.strip():
            unusable.append(f"{name} {' '.join(argv)}: rc={result.returncode}")
    assert not unusable, "unusable flag value not refused with exit 2: " + ", ".join(unusable)
    print(
        f"OK: {len(scripts)} discovered Python CLIs provide help, refuse unknown flags "
        f"and unusable values with exit 2, and are documented"
    )


if __name__ == "__main__":
    main()
