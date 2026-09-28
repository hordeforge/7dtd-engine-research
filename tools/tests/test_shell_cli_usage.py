#!/usr/bin/env python3
"""Require side-effect-free help from supported shell entry points."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

TOOLS = _common.TOOLS
SCRIPTS = (
    "build.sh",
    "cecil-pin.sh",
    "post-update.sh",
    "regen.sh",
    "release.sh",
    "stock-sync.sh",
    "parity/drift-check.sh",
    "steam/fetch_version.sh",
)


def header_comment(path: str) -> list[str]:
    """The script's leading comment block, as `--help` must print it."""
    lines: list[str] = []
    with open(path, encoding="utf-8") as handle:
        for index, line in enumerate(handle):
            if index == 0:
                continue
            if not line.startswith("#"):
                break
            lines.append(line[1:].removeprefix(" ").rstrip())
    return lines


def main() -> None:
    bad = []
    for relative in SCRIPTS:
        path = TOOLS / relative
        result = _common.run_cmd(
            [path, "--help"], text=True, encoding="utf-8", errors="replace", capture_output=True
        )
        if result.returncode != 0 or not result.stdout.strip():
            bad.append(f"{relative}: rc={result.returncode}, stderr={result.stderr.strip()!r}")
            continue
        # A stale line range used to spill the source below the comment block
        # into the help text; the whole block must still be printed, and nothing
        # past its end.
        printed = result.stdout.splitlines()
        if printed != header_comment(str(path)):
            bad.append(f"{relative}: help is not the header comment block:\n" + "\n".join(printed))
    assert not bad, "\n".join(bad)
    assert _common.run_cmd([TOOLS / "build.sh", "--bad"], capture_output=True).returncode == 2
    assert _common.run_cmd([TOOLS / "regen.sh", "--bad"], capture_output=True).returncode == 2
    assert _common.run_cmd([TOOLS / "post-update.sh", "--bad"], capture_output=True).returncode == 2

    # The opt-in Steam side of the post-update path must stay documented: the
    # default run is offline, so a reader only discovers --steam from the help.
    help_text = _common.run_cmd(
        [TOOLS / "post-update.sh", "--help"],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    ).stdout
    assert "--steam" in help_text, help_text
    assert "offline" in help_text, help_text
    print(f"OK: {len(SCRIPTS)} shell CLIs provide side-effect-free help")


if __name__ == "__main__":
    main()
