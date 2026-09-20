#!/usr/bin/env python3
"""Every maintained Python CLI provides dependency-free help, and is documented.

The tool list is discovered from the AST (`_common.argparse_clis`), not kept by
hand: a new CLI is covered the moment it exists, which is how `facts.py` and the
link/pin helpers were found absent from the old hand-kept list. Each discovered
script must print help for `--help` without importing its optional runtime
dependencies, and must be named in `tools/README.md`.

Usage: python3 tools/tests/test_python_cli_usage.py
"""

from __future__ import annotations

import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

README = _common.TOOLS / "README.md"


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
        result = subprocess.run(
            [sys.executable, str(path), "--help"], text=True, capture_output=True
        )
        if result.returncode != 0 or "usage:" not in result.stdout.lower():
            broken.append(
                f"{relative}: rc={result.returncode}, stderr={result.stderr.strip()[:160]!r}"
            )
        if path.name not in readme:
            undocumented.append(relative)
    assert not broken, "\n".join(broken)
    assert not undocumented, "CLIs missing from tools/README.md: " + ", ".join(undocumented)
    print(f"OK: {len(scripts)} discovered Python CLIs provide help and are documented")


if __name__ == "__main__":
    main()
