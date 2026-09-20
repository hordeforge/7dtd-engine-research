#!/usr/bin/env python3
"""research_diff.py: parsing, rendering, and CLI contract.

DLL-free: the lens parsers and the report renderer are exercised directly with
fixtures, and the CLI cases that need no assembly are run end to end. The live
b9->b10 run is a research artifact, not a CI assertion (no game bytes in CI).

Usage: python3 tools/tests/test_research_diff.py
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

TOOL = _common.TOOLS / "research_diff.py"


def load_module() -> Any:
    spec = importlib.util.spec_from_file_location("research_diff", TOOL)
    assert spec is not None, TOOL
    assert spec.loader is not None, TOOL
    module: Any = importlib.util.module_from_spec(spec)
    sys.modules["research_diff"] = module  # dataclasses resolve cls.__module__ there
    spec.loader.exec_module(module)
    return module


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(TOOL), *args], text=True, capture_output=True, check=False
    )


def load_sibling(name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(f"{name}.py"))
    assert spec is not None, name
    assert spec.loader is not None, name
    sibling: Any = importlib.util.module_from_spec(spec)
    sys.modules[name] = sibling
    spec.loader.exec_module(sibling)
    return sibling


def source(module: Any, label: str, facts: dict[str, Any], buildid: str | None = None) -> Any:
    return module.Source(
        label=label,
        path=Path(f"/nonexistent/{label}.dll"),
        sha256="a" * 64,
        size=100,
        facts=facts,
        buildid=buildid,
    )


def main() -> None:
    module = load_module()

    help_run = run("--help")
    assert help_run.returncode == 0, help_run
    assert "usage:" in help_run.stdout.lower(), help_run

    assert run("--old", "a.dll").returncode == 2
    missing = run("--old", "/nonexistent/a.dll", "--new", "/nonexistent/b.dll")
    assert missing.returncode == 2, missing
    assert "dll not found" in missing.stderr, missing.stderr

    # Facts flatten skips the volatile stamp and the input filename.
    flat = module.flatten(
        {"asm": "a.dll", "extracted_utc": "x", "version": {"build": 9}, "behaviour": {"a": 1}}
    )
    assert flat == {"version.build": 9, "behaviour.a": 1}, flat
    counts, lines = module.diff_maps(flat, {"version.build": 10, "behaviour.a": 2})
    assert counts == {"added": 0, "removed": 0, "changed": 2}, counts
    assert lines == ["~ behaviour.a: 1 -> 2", "~ version.build: 9 -> 10"], lines

    pairs = module.parse_pairs("TopLevelTypes                = 4426\nno equals here\nA.B=1")
    assert pairs == {"TopLevelTypes": "4426", "A.B": "1"}, pairs

    methods = module.parse_methods("T::M(Int32,String)\nnoise\nU::N()")
    assert methods == {"T::M": "Int32,String", "U::N": ""}, methods
    changed, _ = module.diff_maps(methods, {"T::M": "Int32", "U::N": ""})
    assert changed["changed"] == 1, changed

    capped = module.cap([f"line{i}" for i in range(50)], 3)
    assert capped.splitlines() == ["line0", "line1", "line2", "... (47 more)"], capped
    assert module.cap([], 3) == "none"

    old = source(module, "b9", {"version": {"display": "V 3.2.0", "stock_wire": "V3.2.0 b9"}}, "1")
    new = source(
        module, "b10", {"version": {"display": "V 3.2.0", "stock_wire": "V3.2.0 b10"}}, "2"
    )
    sections = [
        module.Section("Stock facts (StockFacts.exe)", {"changed": 1}, "~ version.build: 9 -> 10"),
        module.Section("Census (Census.exe)", {"changed": 0}, "none"),
        module.Section("Method signatures (MethodList.exe)", {"changed": 0}, "none"),
        module.Section("Enum members (EnumList.exe)", {"changed": 0}, "none"),
        module.Section("Method bodies (asm_body_diff.py)", {"changed": 0}, "none"),
        module.Section(
            "Wire parity (parity_diff.py)", {}, "", note="not measured: pass --parity-old"
        ),
    ]
    report = module.report_markdown(old, new, sections, "2026-01-01T00:00:00Z", ["--old", "a"])
    assert "# Build diff: b9 -> b10" in report, report
    assert "drift: yes (stock facts 1, census 0" in report, report
    assert "| Steam build | 1 | 2 |" in report, report
    assert "## 6. Wire parity" in report, report
    assert "not measured" in report, report
    assert "\n\n## 1. Stock facts" in report, report
    assert "python3 tools/research_diff.py --old a" in report, report

    quiet = module.report_markdown(
        old, new, [module.Section("Stock facts (StockFacts.exe)", {}, "none")], "t", []
    )
    assert "drift: no" in quiet, quiet

    # Depot-manifest lens: fixture manifests built with the sibling encoder.
    encoder = load_sibling("test_steam_manifest")
    with tempfile.TemporaryDirectory(prefix="research_diff_", dir=_common.scratch_dir()) as tmp:
        root = Path(tmp)
        old_manifest = root / "294422_1.manifest"
        new_manifest = root / "294422_2.manifest"
        other_depot = root / "294421_2.manifest"
        old_manifest.write_bytes(encoder.manifest([encoder.entry("Data\\a.bin", b"old")]))
        new_manifest.write_bytes(
            encoder.manifest(
                [encoder.entry("Data\\a.bin", b"new"), encoder.entry("Data\\b.bin", b"added")]
            )
        )
        other_depot.write_bytes(new_manifest.read_bytes())
        depot = module.lens_depot(old_manifest, new_manifest, 10)
        assert depot.counts == {"added": 1, "removed": 0, "changed": 1}, depot.counts
        assert "gid 1 -> 2" in depot.body, depot.body
        assert "Data\\a.bin" in depot.body, depot.body

        unmeasured = module.lens_depot(None, None, 10)
        assert unmeasured.counts == {}, unmeasured
        assert "not measured" in (unmeasured.note or ""), unmeasured.note
        mismatched = module.lens_depot(old_manifest, other_depot, 10)
        assert "depot 294422 != 294421" in (mismatched.note or ""), mismatched.note

        sections.append(depot)
        with_depot = module.report_markdown(
            old, new, sections, "2026-01-01T00:00:00Z", ["--old", "a"]
        )
        assert "## 7. Depot manifest (steam_manifest.py)" in with_depot, with_depot
        assert "depot manifest 2" in with_depot, with_depot

    pins = {"studied": {"dll_sha256": "b" * 64, "buildid": "42", "branch": "public"}}
    assert module.buildid_for("b" * 64, pins) == "42"

    # --pair resolution helpers (pure): label matching and candidate filtering.
    facts_b9 = {"version": {"display": "V 3.2.0", "stock_wire": "V3.2.0 b9", "build": 9}}
    assert module.label_matches("b9", facts_b9), facts_b9
    assert module.label_matches("V3.2.0 b9", facts_b9), facts_b9
    assert not module.label_matches("b10", facts_b9), facts_b9
    assert not module.label_matches("", facts_b9), facts_b9
    with tempfile.TemporaryDirectory(
        prefix="research_diff_pair_", dir=_common.scratch_dir()
    ) as tmp:
        game = Path(tmp)
        (game / "Assembly-CSharp.dll").write_bytes(b"x" * 1_100_000)
        (game / "Assembly-CSharp.dll.re_stock_bak").write_bytes(b"y" * 1_100_000)
        (game / "Assembly-CSharp.dll.re_height_expanded").write_bytes(b"tiny note")
        names = [p.name for p in module.candidate_dlls(game)]
        assert names == ["Assembly-CSharp.dll", "Assembly-CSharp.dll.re_stock_bak"], names

    assert run("--pair", "nocolon").returncode == 2
    assert run("--pair", "b9:b10", "--old", "x.dll").returncode == 2
    assert run("--old", "a.dll").returncode == 2

    # Live --pair run when this machine keeps the previous build beside the live one.
    asm = _common.find_asm()
    backup = asm.with_name(asm.name + ".re_stock_bak") if asm else None
    if asm is None or backup is None or not backup.is_file():
        print("note: live --pair check skipped (no retained stock backup)")
    else:
        pair_run = run("--pair", "b9:b10", "--out", "-")
        assert pair_run.returncode == 0, (pair_run.stdout[-500:], pair_run.stderr)
        assert "pair: b9 ->" in pair_run.stdout, pair_run.stdout
        assert "pair: b10 ->" in pair_run.stdout, pair_run.stdout
        assert "## 7. Depot manifest" in pair_run.stdout, pair_run.stdout
        assert "no change\n\n```\n=== PACKAGE DIFF ===\nadded (0)" in pair_run.stdout, (
            pair_run.stdout
        )
    assert module.buildid_for("c" * 64, pins) is None

    print("OK: research_diff parsers, renderer, and CLI contract hold")


if __name__ == "__main__":
    main()
