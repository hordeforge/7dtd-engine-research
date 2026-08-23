#!/usr/bin/env python3
"""Structural proof: dedicated RE coverage docs + dump evidence exist and are IL-backed.

Drives real repo artifacts under 7dtd-engine-research/docs and 7dtd-engine-research/il (no hard-coded
game constants as the pass condition; asserts files and dump-backed markers).

The tracked-content checks (docs, legacy dumper sources) always run. The
git-ignored il/ dump-set checks only run when the local dedicated
Assembly-CSharp.dll is available to regenerate them; on machines without the
game install they SKIP instead of failing (dumps are machine-local artifacts).
With the DLL present but dumps stale/missing they still FAIL.

Usage: python3 tools/tests/test_dedi_coverage_docs.py
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]  # 7dtd-engine-research
RESEARCH = ROOT
DOCS = RESEARCH / "docs"
IL = RESEARCH / "il"
FACTS = RESEARCH / "tools" / "data" / "stock_facts.json"

FAMILY_DOCS = [
    "architecture-map.md",
    "loop.md",
    "loop-gmupdate.md",
    "managers.md",
    "entity-ai.md",
    "protocol.md",
    "protocol-packages.md",
    "protocol-frames.md",
    "world-chunks.md",
    "terrain-height.md",
    "save-region.md",
    "light-mesh-water.md",
    "console-commands.md",
    "residuals.md",
    "closed-gaps.md",
    "engine-limitations.md",
    "coverage.md",
    "re-methodology.md",
    "INDEX.md",
]

# Product RealEarth docs (not under 7dtd-engine-research/docs). The sibling repo is
# absent in a single-repo CI checkout; its checks run locally only.
PRODUCT_DOCS = ROOT.parent / "7dtd-realearth" / "docs"
PRODUCT_PRESENT = PRODUCT_DOCS.is_dir()
PRODUCT_REALEARTH = [
    "realearth-runtime.md",
    "realearth-surfaces.md",
    "realearth-review.md",
]

DEDICATED_DUMPS = [
    "dedi-complete-v3.1.0/DEDI_COMPLETE_auto.md",
    "deep-v3.1.0/GameManager_il.txt",
    "deep-v3.1.0/NetPackage_il.txt",
    "deep-v3.1.0/World_il.txt",
    "terrain-v3.1.0/TERRAIN_auto.md",
    "realearth-surfaces-v3.1.0/REALEARTH_SURFACES_auto.md",
]

TOOLS = [
    "DumpDediComplete.cs",
    "DumpTerrain.cs",
    "DumpRealEarthSurfaces.cs",
]


def has_il_backed_claim(text: str) -> bool:
    if "7dtd-engine-research/il/" in text or "../il/" in text or "il/" in text:
        if re.search(
            r"IL\s*=\s*\d+|IL=\d+|y\s*>>\s*2|ldc\.i4|ChunkBlockYDim|ticksPerSecond",
            text,
        ):
            return True
    return False


def is_dump_marker(text: str) -> bool:
    return (
        "DEDI_COMPLETE_auto.md" in text
        or "REALEARTH_SURFACES_auto.md" in text
        or "TERRAIN_auto.md" in text
    )


# Detector-liveness witnesses: each banned open-gap phrase must match its own
# stale sentence, and the IL-claim detector must fire on a real claim and stay
# quiet on plain narrative. Without these the gate could stay green through a
# regex typo (a detector that never fires is a test that always passes).
BAN_WITNESSES = {
    "WorldState still open": "The WorldState surface is still partially open.",
    "Origin dedicated wrong": "the Dedicated path is **not a no-op** here.",
    "stale GAME_LOOP gap #8": "see GAME_LOOP open gap #8 for details.",
}

IL_CLAIM_POSITIVE = (
    "gmUpdate measured IL = 4210 (../il/deep-v3.1.0/GameManager_il.txt)"
)
IL_CLAIM_POSITIVE_MARKER = (
    "Full inventory: ../il/dedi-complete-v3.1.0/DEDI_COMPLETE_auto.md"
)
IL_CLAIM_NEGATIVE = (
    "This family describes behavior only; numbers live in the inventories."
)


def self_test_detectors(fails: list[str]) -> None:
    for pat, label in ban_pattern_specs():
        if label not in BAN_WITNESSES:
            fails.append(f"self-test: no witness for banned phrase ({label})")
        elif not re.search(pat, BAN_WITNESSES[label]):
            fails.append(f"self-test: ban pattern cannot fire ({label})")
    if not has_il_backed_claim(IL_CLAIM_POSITIVE):
        fails.append("self-test: IL-claim detector missed an IL= + il/ path claim")
    if not has_il_backed_claim(IL_CLAIM_POSITIVE_MARKER):
        fails.append("self-test: IL-claim detector missed a dump-marker path")
    if has_il_backed_claim(IL_CLAIM_NEGATIVE):
        fails.append("self-test: IL-claim detector fired on plain narrative")


def ban_pattern_specs() -> list[tuple[str, str]]:
    """(regex, label) pairs for open-gap language that must not reappear."""
    return [
        (r"(?i)WorldState.*still partially open", "WorldState still open"),
        (r"(?i)Dedicated path is \*\*not a no-op\*\*", "Origin dedicated wrong"),
        (r"(?i)GAME_LOOP open gap #8", "stale GAME_LOOP gap #8"),
    ]


def main() -> int:
    tools = _common.TOOLS / "legacy"
    fails: list[str] = []
    notes: list[str] = []

    asm_present = _common.find_asm() is not None

    self_test_detectors(fails)

    for name in FAMILY_DOCS:
        p = DOCS / name
        if not p.is_file():
            fails.append(f"missing family doc: {p}")
            continue
        txt = p.read_text(encoding="utf-8", errors="replace")
        if len(txt) < 300:
            fails.append(f"family doc too short (<300 bytes): {name}")
        if name != "INDEX.md":
            if not has_il_backed_claim(txt) and not is_dump_marker(txt):
                fails.append(f"family doc lacks IL or dump evidence reference: {name}")

        for pat, label in ban_pattern_specs():
            if re.search(pat, txt):
                fails.append(f"{name} re-introduced banned open-gap language ({label})")

    # Dumps are local artifacts generated from Assembly-CSharp.dll via tools/.
    # When Assembly-CSharp.dll is available locally, missing dumps are an error.
    # On CI / single-repo checkouts without the game install, we skip.
    if asm_present:
        for rel in DEDICATED_DUMPS:
            p = IL / rel
            if not p.is_file():
                fails.append(f"missing dedicated dump artifact: {p}")
            elif p.stat().st_size < 1000:
                fails.append(f"dedicated dump artifact too small: {p}")
    else:
        notes.append("game assembly absent: skipping il/ dump-set size assertions")

    if not FACTS.is_file():
        fails.append(f"missing machine stock facts: {FACTS}")

    for tname in TOOLS:
        tp = tools / tname
        if not tp.is_file():
            fails.append(f"missing Mono.Cecil dump tool: {tp}")

    for old in ["A21", "Alpha 21", "a21"]:
        for name in FAMILY_DOCS:
            text = (DOCS / name).read_text(encoding="utf-8", errors="replace")
            if old in text:
                fails.append(f"{name} still references {old}")

    # RealEarth product docs live under 7dtd-realearth/docs (not 7dtd-engine-research/docs)
    if PRODUCT_PRESENT:
        for name in PRODUCT_REALEARTH:
            p = PRODUCT_DOCS / name
            if not p.is_file() or p.stat().st_size < 200:
                fails.append(f"missing product RealEarth doc: {p}")
            if (DOCS / name).exists():
                fails.append(f"RealEarth doc still under 7dtd-engine-research/docs: {name}")

    # research INDEX should not own product RealEarth as primary
    idx = (DOCS / "INDEX.md").read_text(encoding="utf-8", errors="replace")
    if "generic engine" not in idx.lower() and "Generic engine" not in idx:
        fails.append("research INDEX missing generic-engine ownership language")
    if "7dtd-realearth/docs" not in idx:
        fails.append("research INDEX should link product RealEarth docs")

    for n in notes:
        print("NOTE:", n)
    if fails:
        print("FAIL:")
        for f in fails:
            print(" -", f)
        return 1

    print("OK: all dedicated RE coverage docs and dump references valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
