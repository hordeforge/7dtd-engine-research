#!/usr/bin/env python3
"""drift-check.sh must compare the wire axis against the committed snapshot.

A fresh checkout has no `BASELINE_DIR`, and the old behaviour was to write one
and compare nothing, so the first `make drift` after cloning said "baseline
created" and stopped. The wire axis is now compared against the committed
`workspace/outputs/parity/parity_b10.json`, and this test pins all three
behaviours: fresh baseline + committed snapshot (compared), a perturbed
snapshot (drift, exit 1), and no snapshot at all (baseline created, exit 0).

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
        assert "comparing the wire axis against the committed snapshot" in fresh.stdout, (
            fresh.stdout
        )
        assert "drift: NONE (build matches the committed wire baseline)" in fresh.stdout, (
            fresh.stdout
        )

        perturbed = json.loads(COMMITTED.read_text(encoding="utf-8"))
        package = sorted(perturbed["packages"])[0]
        perturbed["packages"][package]["write"] += "WriteSingle;"
        perturbed_path = root / "perturbed.json"
        perturbed_path.write_text(json.dumps(perturbed), encoding="utf-8")
        drifted = run(asm, root / "cb2", perturbed_path)
        assert drifted.returncode == 1, (drifted.stdout[-400:], drifted.stderr[-400:])
        assert "drift: DETECTED against the committed wire baseline" in drifted.stdout, (
            drifted.stdout
        )
        assert package in drifted.stdout, drifted.stdout
        # The update advice names the baseline actually in force.
        assert str(perturbed_path) in drifted.stdout, drifted.stdout

        absent = run(asm, root / "cb3", root / "absent.json")
        assert absent.returncode == 0, (absent.stdout[-400:], absent.stderr[-400:])
        assert "no comparison this run" in absent.stdout, absent.stdout

    print(
        "OK: drift-check compares the committed wire baseline on a fresh checkout, "
        "flags a perturbed one, and stays quiet with none"
    )


if __name__ == "__main__":
    main()
