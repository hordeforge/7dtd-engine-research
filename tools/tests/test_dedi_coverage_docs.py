#!/usr/bin/env python3
"""Structural proof: dedicated RE coverage docs + dump evidence exist and are IL-backed.

Drives real repo artifacts under 7dtd-research/docs and 7dtd-research/il (no hard-coded
game constants as the pass condition; asserts files and dump-backed markers).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RESEARCH = ROOT / "7dtd-research"
DOCS = RESEARCH / "docs"
IL = RESEARCH / "il"
FACTS = RESEARCH / "tools" / "data" / "stock_facts.json"


def dump_label_suffix() -> str:
    """Folder suffix from stock_facts display, e.g. V X.Y.Z -> vX.Y.Z."""
    if FACTS.is_file():
        v = json.loads(FACTS.read_text(encoding="utf-8"))["version"]
        disp = v.get("display", "V 0.0.0").replace("V ", "").strip()
        return f"v{disp}"
    # Fallback only when facts missing (tests still need a label).
    return "v0.0.0"


def dump_sets_for_pin() -> list[str]:
    suf = dump_label_suffix()
    bases = [
        "deep",
        "deeper",
        "gaps",
        "loop-complete",
        "terrain",
        "realearth-surfaces",
        "dedi-complete",
    ]
    return [f"{b}-{suf}" for b in bases]

FAMILY_DOCS = [
    "coverage.md",
    "loop.md",
    "world-chunks.md",
    "terrain-height.md",
    "entity-ai.md",
    "network.md",
    "save-region.md",
    "managers.md",
    "light-mesh-water.md",
    "residuals.md",
    "INDEX.md",
]

# Product RealEarth docs (not under 7dtd-research/docs). The sibling repo is
# absent in a single-repo CI checkout; its checks run locally only.
PRODUCT_DOCS = ROOT / "7dtd-realworld" / "docs"
PRODUCT_PRESENT = PRODUCT_DOCS.is_dir()
PRODUCT_REALEARTH = [
    "realearth-runtime.md",
    "realearth-surfaces.md",
    "realearth-review.md",
]

# The corpus tracks the latest release only; directory names follow stock_facts.
# gmUpdate and terrain-stock folded into loop-complete and terrain historically.
DUMP_SETS = dump_sets_for_pin()

TOOLS = [
    "DumpDeep.cs",
    "DumpDeeper.cs",
    "DumpGaps.cs",
    "DumpLoopComplete.cs",
    "DumpTerrain.cs",
    "DumpRealEarthSurfaces.cs",
    "DumpDediComplete.cs",
]


def has_il_backed_claim(text: str) -> bool:
    if "7dtd-research/il/" in text or "../il/" in text or "il/" in text:
        if re.search(
            r"IL\s*=\s*\d+|IL=\d+|y\s*>>\s*2|ldc\.i4|ChunkBlockYDim|ticksPerSecond",
            text,
        ):
            return True
        if re.search(r"_il\.txt|_calls\.md|DEDI_COMPLETE|TERRAIN_auto|SAVE_LIGHT", text):
            return True
    if re.search(r"\bIL\s*=\s*\*?\*?\d+|IL=\d+", text):
        return True
    return bool(
        re.search(r"\bIL\b.*\d{2,}", text)
        and ("dump" in text.lower() or "il/" in text.lower() or "measured" in text.lower())
    )


def main() -> int:
    tools = ROOT / "7dtd-research" / "tools" / "legacy"
    fails: list[str] = []

    for name in FAMILY_DOCS:
        p = DOCS / name
        if not p.is_file() or p.stat().st_size < 200:
            fails.append(f"missing/tiny doc: {p}")
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        if name in ("INDEX.md", "residuals.md", "coverage.md"):
            continue
        if not has_il_backed_claim(text):
            if not re.search(r"IL\s*=\s*\d+|IL=\d+", text):
                fails.append(f"no IL-backed claim: {name}")

    cov = (DOCS / "coverage.md").read_text(encoding="utf-8", errors="replace")
    for fam in (
        "Frame",
        "chunk",
        "Terrain",
        "AI",
        "Network",
        "Save",
        "Origin",
        "Manager",
        "Light",
        "ModEvents",
    ):
        if fam.lower() not in cov.lower():
            fails.append(f"coverage hub missing family keyword: {fam}")

    for ds in DUMP_SETS:
        d = IL / ds
        if not d.is_dir():
            fails.append(f"missing dump set dir: {ds}")
            continue
        if sum(1 for _ in d.iterdir()) < 1:
            fails.append(f"empty dump set: {ds}")

    dedi_dir = f"dedi-complete-{dump_label_suffix()}"
    auto = IL / dedi_dir / "DEDI_COMPLETE_auto.md"
    if not auto.is_file():
        fails.append(f"missing {dedi_dir}/DEDI_COMPLETE_auto.md")
    else:
        t = auto.read_text(encoding="utf-8", errors="replace")
        for needle in (
            "ModEvents",
            "NetPackage",
            "WorldState",
            "ChunkBlockYDim",
            "Origin.FixedUpdate",
        ):
            if needle not in t:
                fails.append(f"DEDI_COMPLETE_auto missing {needle}")

    # deeper.md must mirror the regenerated dump's DEEPER.md body (stale-pin guard:
    # the doc once carried V3.0.1 IL sizes under a v3.1.0 dump pointer).
    deeper_dump = IL / f"deeper-{dump_label_suffix()}" / "DEEPER.md"
    deeper_doc = DOCS / "inventories" / "deeper.md"
    if not deeper_dump.is_file():
        fails.append(f"missing {deeper_dump}")
    elif deeper_doc.is_file():
        doc_t = deeper_doc.read_text(encoding="utf-8", errors="replace")
        dump_t = deeper_dump.read_text(encoding="utf-8", errors="replace")
        i1, i2 = doc_t.find("## 1."), dump_t.find("## 1.")
        if i1 < 0 or i2 < 0 or doc_t[i1:] != dump_t[i2:]:
            fails.append(
                "docs/inventories/deeper.md stale vs the deeper dump's DEEPER.md (regenerate from the dump)"
            )

    # gaps.md mirrors GAPS_CLOSED.md with raw-IL bodies (>4 lines) elided for
    # publication (AGENTS no-bulk-IL rule); the rest must match the regenerated
    # dump, so a stale V3.0.1-era body (old IL= sizes) fails here.
    gaps_dump = IL / f"gaps-{dump_label_suffix()}" / "GAPS_CLOSED.md"
    gaps_doc = DOCS / "inventories" / "gaps.md"
    if not gaps_dump.is_file():
        fails.append(f"missing {gaps_dump}")
    elif gaps_doc.is_file():
        dump_lines = gaps_dump.read_text(encoding="utf-8", errors="replace").splitlines()
        elided, cur, in_fence, il_lines = [], [], False, 0
        for l in dump_lines:
            if l.strip().startswith("```"):
                if in_fence:
                    if il_lines > 4:
                        elided.append("```")
                        elided.append("*(raw IL listing elided for publication - regenerate locally with the Cecil dump tools; see INDEX.md)*")
                        elided.append("```")
                    else:
                        elided.append("```")
                        elided.extend(cur)
                        elided.append("```")
                in_fence = not in_fence
                cur, il_lines = [], 0
                continue
            if in_fence:
                cur.append(l)
                if l.strip().startswith("IL_"):
                    il_lines += 1
            else:
                elided.append(l)
        if in_fence:
            if il_lines > 4:
                elided.append("```")
                elided.append("*(raw IL listing elided for publication - regenerate locally with the Cecil dump tools; see INDEX.md)*")
                elided.append("```")
            else:
                elided.append("```")
                elided.extend(cur)
                elided.append("```")
        g1 = gaps_doc.read_text(encoding="utf-8", errors="replace").find("## 1.")
        g2 = next((k for k, l in enumerate(elided) if l.startswith("## 1.")), -1)
        if g1 < 0 or g2 < 0 or gaps_doc.read_text(encoding="utf-8", errors="replace")[g1:] != "\n".join(elided[g2:]) + "\n":
            fails.append(
                "docs/inventories/gaps.md stale vs the gaps dump's GAPS_CLOSED.md (regenerate with the >4-line IL elision policy)"
            )

    # opt-scan.md and loop-complete.md mirror their dump masters verbatim (the
    # masters carry no raw-IL bodies, so no elision policy applies); a stale
    # V3.0.1-era body (old IL= sizes) fails here.
    mirror_pairs = {
        "opt-scan.md": IL / f"opt-scan-{dump_label_suffix()}" / "OPT_SCAN.md",
        "loop-complete.md": IL / f"loop-complete-{dump_label_suffix()}" / "inventory-loop-complete.md",
    }
    for doc_name, master in mirror_pairs.items():
        doc_p = DOCS / "inventories" / doc_name
        if not master.is_file():
            fails.append(f"missing {master}")
        elif doc_p.is_file():
            doc_t = doc_p.read_text(encoding="utf-8", errors="replace")
            mas_t = master.read_text(encoding="utf-8", errors="replace")
            d1 = doc_t.find("\n- **") if doc_name == "opt-scan.md" else doc_t.find("\n## ")
            m1 = mas_t.find("\n- **") if doc_name == "opt-scan.md" else mas_t.find("\n## ")
            if d1 < 0 or m1 < 0 or doc_t[d1 + 1 :] != mas_t[m1 + 1 :]:
                fails.append(
                    f"docs/inventories/{doc_name} stale vs {master.name} (regenerate from the dump)"
                )

    # every il/ reference in the docs must resolve (markdown links + bare file
    # mentions); il/ is git-ignored, so this gate runs locally only.
    il_ref_pat = re.compile(r"il/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*\.(?:md|txt)")
    link_pat = re.compile(r"\]\(([^)]*?il/[^)]*)\)")
    seen = set()
    for p in sorted(DOCS.glob("*.md")) + sorted((DOCS / "inventories").glob("*.md")):
        text = p.read_text(encoding="utf-8", errors="replace")
        for m in link_pat.finditer(text):
            target = (p.parent / m.group(1)).resolve()
            if target not in seen:
                seen.add(target)
                if not target.exists():
                    fails.append(f"{p.name}: il/ link -> {m.group(1)} missing")
            text = text.replace(m.group(0), "")
        for m in il_ref_pat.finditer(text):
            tok = m.group(0)
            if tok in seen:
                continue
            seen.add(tok)
            if not (IL / tok.split("il/", 1)[1]).exists():
                fails.append(f"{p.name}: bare il/ mention -> {tok} missing")

    for tool in TOOLS:
        if not (tools / tool).is_file():
            fails.append(f"missing dump tool: {tool}")

    res = (DOCS / "residuals.md").read_text(encoding="utf-8", errors="replace")
    if "unmapped" not in res.lower() and "closed" not in res.lower():
        fails.append("residuals missing coverage-closed language")
    if re.search(r"(?i)managed surface.*(TODO|not reversed|not started)", res):
        fails.append("residuals still marks managed surface incomplete")

    ban_patterns = [
        (r"(?i)WorldState.*still partially open", "WorldState still open"),
        (r"(?i)Dedicated path is \*\*not a no-op\*\*", "Origin dedicated wrong"),
        (r"(?i)GAME_LOOP open gap #8", "stale GAME_LOOP gap #8"),
    ]
    ban_targets = [("terrain-height.md", DOCS), ("loop.md", DOCS)]
    if PRODUCT_PRESENT:
        ban_targets.append(("realearth-surfaces.md", PRODUCT_DOCS))
    for name, base in ban_targets:
        text = (base / name).read_text(encoding="utf-8", errors="replace")
        for pat, label in ban_patterns:
            if re.search(pat, text):
                fails.append(f"{name}: banned open-gap language ({label})")

    # no leftover old filenames in research docs
    old_names = [
        "GAME_LOOP.md",
        "STRUCTURE_DEEP.md",
        "DEDICATED_ENGINE_COVERAGE.md",
        "SYNTHESIS_deeper.md",
    ]
    for name in FAMILY_DOCS + ["INDEX.md", "coverage.md"]:
        text = (DOCS / name).read_text(encoding="utf-8", errors="replace")
        for old in old_names:
            if old in text:
                fails.append(f"{name} still references {old}")

    # RealEarth product docs live under 7dtd-realworld/docs (not 7dtd-research/docs)
    if PRODUCT_PRESENT:
        for name in PRODUCT_REALEARTH:
            p = PRODUCT_DOCS / name
            if not p.is_file() or p.stat().st_size < 200:
                fails.append(f"missing product RealEarth doc: {p}")
            if (DOCS / name).exists():
                fails.append(f"RealEarth doc still under 7dtd-research/docs: {name}")

    # research INDEX should not own product RealEarth as primary
    idx = (DOCS / "INDEX.md").read_text(encoding="utf-8", errors="replace")
    if "generic engine" not in idx.lower() and "Generic engine" not in idx:
        fails.append("research INDEX missing generic-engine ownership language")
    if "7dtd-realworld/docs" not in idx:
        fails.append("research INDEX should link product RealEarth docs")

    if fails:
        print("FAIL:")
        for f in fails:
            print(" -", f)
        return 1
    print("OK: dedi coverage docs + dump sets + tools present")
    print(f"  docs_checked={len(FAMILY_DOCS)} dump_sets={len(DUMP_SETS)} tools={len(TOOLS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
