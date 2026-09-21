#!/usr/bin/env python3
"""drift-check.sh must compare every axis against the committed baselines.

A fresh checkout has no `BASELINE_DIR`, and the old behaviour was to write one
and compare nothing, so the first `make drift` after cloning said "baseline
created" and stopped. Every axis (census, types, methods, enums, wire) now
compares against `workspace/outputs/baseline/` plus the committed wire snapshot,
and this test pins the behaviours: a fresh baseline dir still reports every axis
against the committed files (NONE for the studied build, which also proves the
committed baselines are not stale), a perturbed snapshot is detected with exit
1, and an axis with no baseline anywhere is reported rather than passed.

Needs mono/mcs, the built tools, the live DLL. SKIPs otherwise.

Usage: python3 tools/tests/test_drift_committed_baseline.py
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

DRIFT = _common.TOOLS / "parity" / "drift-check.sh"
COMMITTED = _common.REPO / "workspace" / "outputs" / "parity" / "parity_b10.json"


def run(asm: Path, baseline: Path, parity: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ | {"BASELINE_DIR": str(baseline), "PARITY_BASELINE": str(parity)}
    return subprocess.run(
        [str(DRIFT), str(asm)], env=env, text=True, capture_output=True, check=False
    )


def main() -> None:
    asm = _common.find_asm()
    if asm is None:
        print("SKIP: dedicated Assembly-CSharp.dll not found")
        return
    bins = ("Census.exe", "FullSurface.exe", "MethodList.exe", "EnumList.exe", "ParitySurface.exe")
    if (
        shutil.which("mono") is None
        or shutil.which("mcs") is None
        or any(not (_common.BIN / name).is_file() for name in bins)
    ):
        print("SKIP: drift-check needs mono, mcs, and the built tools")
        return
    if not COMMITTED.is_file():
        print(f"SKIP: committed snapshot missing: {COMMITTED.name}")
        return

    with tempfile.TemporaryDirectory(prefix="drift_baseline_", dir=_common.scratch_dir()) as tmp:
        root = Path(tmp)

        fresh = run(asm, root / "cb1", COMMITTED)
        assert fresh.returncode == 0, (fresh.stdout[-400:], fresh.stderr[-400:])
        assert "using the committed baseline" in fresh.stdout, fresh.stdout
        for axis in (
            "census",
            "types (added/removed)",
            "methods (added/removed",
            "enum members",
            "NetPackage wire",
        ):
            assert axis in fresh.stdout, (axis, fresh.stdout)
        assert fresh.stdout.count("(committed baseline)") == 5, fresh.stdout
        assert "drift: NONE (build matches baseline)" in fresh.stdout, fresh.stdout
        assert not (root / "cb1" / "surface").exists(), "clean comparison seeded a local baseline"

        perturbed = json.loads(COMMITTED.read_text(encoding="utf-8"))
        package = sorted(perturbed["packages"])[0]
        perturbed["packages"][package]["write"] += "WriteSingle;"
        perturbed_path = root / "perturbed.json"
        perturbed_path.write_text(json.dumps(perturbed), encoding="utf-8")
        drifted = run(asm, root / "cb2", perturbed_path)
        assert drifted.returncode == 1, (drifted.stdout[-400:], drifted.stderr[-400:])
        assert "drift: DETECTED" in drifted.stdout, drifted.stdout
        assert package in drifted.stdout, drifted.stdout
        assert "refresh the baseline that flagged it" in drifted.stdout, drifted.stdout

        # An axis with no baseline anywhere is reported, not passed.
        empty_committed = root / "empty-committed"
        empty_committed.mkdir()
        env = os.environ | {
            "BASELINE_DIR": str(root / "cb3"),
            "PARITY_BASELINE": str(root / "absent.json"),
            "COMMITTED_BASELINE": str(empty_committed),
        }
        unmeasured = subprocess.run(
            [str(DRIFT), str(asm)], env=env, text=True, capture_output=True, check=False
        )
        assert unmeasured.returncode == 2, (unmeasured.stdout[-400:], unmeasured.stderr[-400:])
        assert "no baseline for:" in unmeasured.stderr, unmeasured.stderr
        assert (root / "cb3" / "surface" / "surface-types.md").is_file(), (
            "local baseline not seeded"
        )

    print(
        "OK: drift-check compares every axis against the committed baselines on a fresh "
        "checkout, flags a perturbed one, and reports an axis with no baseline"
    )


if __name__ == "__main__":
    main()
