#!/usr/bin/env python3
"""Build-to-build research diff report.

One command that compares two stock `Assembly-CSharp.dll` builds through every
cheap lens this corpus already has, then writes a single build-stamped Markdown
report: source identity (size + sha256 + version), a drift verdict, and the
per-lens detail. The lenses are the maintained tools, not reimplementations:

  facts    StockFacts.exe      version/sim/network/save/behaviour fields
  census   Census.exe          whole-assembly type/method/IL counts
  metadata FullSurface.exe     per-type kind/base/field/method/IL rows
  methods  MethodList.exe      Type::Method(params) signature surface
  enums    EnumList.exe        Enum.Member=value surface
  bodies   asm_body_diff.py    per-method body hash (catches same-size rewrites)
  parity   parity_diff.py      NetPackage wire snapshots, when both are given
  depot    steam_manifest.py   non-managed content delta (per-file SHA-1)

Usage:
  research_diff.py --old backup.dll --new live.dll
  research_diff.py --old backup.dll --new live.dll --label-old b9 --label-new b10 \
      --buildid-old 24994542 --buildid-new 24994542 --check
  research_diff.py --old a.dll --new b.dll --parity-old old.json --parity-new new.json
  research_diff.py --old a.dll --new b.dll \
      --steam-manifest-old ~/.local/share/Steam/depotcache/294422_<old>.manifest \
      --steam-manifest-new ~/.local/share/Steam/depotcache/294422_<new>.manifest

Exit codes: 0 report written, 1 drift detected (--check), 2 unusable input.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from functools import partial
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parent / "tests"))
sys.path.insert(0, str(Path(__file__).resolve().parent / "parity"))
import _common
from steam_manifest import (
    DEFAULT_DEPOT,
    ManifestError,
    assembly_entry,
    assembly_sha1,
    cached_manifests,
    diff_manifests,
    manifest_for_gid,
    pins_buildids,
    read_manifest,
    roots_from,
    sha1_file,
    steam_log_buildids,
)

TOOLS = _common.TOOLS
REPO = _common.REPO
BIN = _common.BIN
DEFAULT_OUT_DIR = REPO / "workspace" / "outputs" / "diffs"
STEAM_PINS = TOOLS / "data" / "steam_builds.json"

FACTS_SKIP = {"asm", "extracted_utc"}
BODY_SUMMARY_RE = re.compile(
    r"methods bak=(\d+) live=(\d+) added=(\d+) removed=(\d+) body-changed=(\d+)"
)


class SourceError(Exception):
    """A requested artifact could not be resolved."""


@dataclass(frozen=True)
class Source:
    label: str
    path: Path
    sha256: str
    size: int
    facts: dict[str, Any]
    buildid: str | None
    depot: str | None = None
    depot_sha1: str | None = None
    depot_matches: bool | None = None

    @property
    def version(self) -> str:
        return str(self.facts.get("version", {}).get("display", "unknown"))

    @property
    def wire(self) -> str:
        return str(self.facts.get("version", {}).get("stock_wire", "unknown"))


@dataclass
class Section:
    title: str
    counts: dict[str, int] = field(default_factory=dict)
    body: str = ""
    note: str | None = None


def mono_env() -> dict[str, str]:
    env = dict(os.environ)
    env["MONO_PATH"] = str(BIN)
    return env


def run(cmd: list[str], timeout: float = 900.0) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, env=mono_env(), timeout=timeout)


def prereq() -> str | None:
    """Return a fix-instruction message when a lens prerequisite is missing."""
    missing = [
        name
        for name in (
            "StockFacts.exe",
            "Census.exe",
            "FullSurface.exe",
            "MethodList.exe",
            "EnumList.exe",
        )
        if not (BIN / name).is_file()
    ]
    if missing:
        return (
            "bin tools not built: " + ", ".join(missing) + " (cd tools && ./build.sh --skip-legacy)"
        )
    if shutil.which("mono") is None:
        return "mono not on PATH (the C# lenses need Mono)"
    return None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_steam_pins() -> dict[str, Any]:
    try:
        with STEAM_PINS.open(encoding="utf-8") as fh:
            pins: Any = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return {}
    return pins if isinstance(pins, dict) else {}


def buildid_for(sha: str, pins: dict[str, Any]) -> str | None:
    """The Steam build id whose studied DLL sha256 matches, when the pin has one."""
    studied = pins.get("studied")
    if isinstance(studied, dict) and studied.get("dll_sha256") == sha and studied.get("buildid"):
        return str(studied["buildid"])
    return None


def depot_provenance(dll: Path, manifest_path: Path | None) -> tuple[str, str, bool] | None:
    """Steam's own SHA-1 for this DLL from a depot manifest, and whether it matches.

    This is the check that says "the bytes I diffed are the bytes Steam shipped":
    the manifest entry for Managed/Assembly-CSharp.dll against the local file.
    """
    if manifest_path is None:
        return None
    entry = assembly_entry(read_manifest(manifest_path))
    if entry is None or entry.sha1 is None:
        return None
    return manifest_path.name, entry.sha1, entry.sha1 == sha1_file(dll)


def extract_facts(dll: Path, tmp: Path, name: str) -> dict[str, Any]:
    out = tmp / f"facts_{name}.json"
    proc = run(["mono", str(BIN / "StockFacts.exe"), str(dll), str(out)])
    if proc.returncode != 0 or not out.is_file():
        raise RuntimeError(f"StockFacts.exe failed on {dll}: {proc.stderr.strip() or proc.stdout}")
    with out.open(encoding="utf-8") as fh:
        facts: Any = json.load(fh)
    if not isinstance(facts, dict):
        raise RuntimeError(f"StockFacts.exe wrote a non-object to {out}")
    return facts


def load_source(
    path: Path, label: str | None, buildid: str | None, tmp: Path, name: str, pins: dict[str, Any]
) -> Source:
    facts = extract_facts(path, tmp, name)
    sha = sha256_file(path)
    wire = str(facts.get("version", {}).get("stock_wire", "unknown"))
    return Source(
        label=label or wire.replace(" ", "-"),
        path=path,
        sha256=sha,
        size=path.stat().st_size,
        facts=facts,
        buildid=buildid or buildid_for(sha, pins),
    )


def flatten(value: Any, prefix: str = "") -> dict[str, Any]:
    flat: dict[str, Any] = {}
    if isinstance(value, dict):
        for key, item in value.items():
            if not prefix and key in FACTS_SKIP:
                continue
            flat.update(flatten(item, f"{prefix}.{key}" if prefix else str(key)))
    elif isinstance(value, list):
        flat[prefix] = json.dumps(value, sort_keys=True)
    else:
        flat[prefix] = value
    return flat


def diff_maps(old: dict[str, Any], new: dict[str, Any]) -> tuple[dict[str, int], list[str]]:
    counts = {"added": 0, "removed": 0, "changed": 0}
    lines: list[str] = []
    for key in sorted(set(old) | set(new)):
        if key not in old:
            counts["added"] += 1
            lines.append(f"+ {key} = {new[key]}")
        elif key not in new:
            counts["removed"] += 1
            lines.append(f"- {key} = {old[key]}")
        elif old[key] != new[key]:
            counts["changed"] += 1
            lines.append(f"~ {key}: {old[key]} -> {new[key]}")
    return counts, lines


def parse_pairs(text: str) -> dict[str, str]:
    """Parse `key = value` (Census) or `key=value` (EnumList) lines."""
    pairs: dict[str, str] = {}
    for line in text.splitlines():
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if key:
            pairs[key] = value
    return pairs


def parse_methods(text: str) -> dict[str, str]:
    """Type::Method(params) -> key Type::Method, value params (signature lens)."""
    methods: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if "::" not in line:
            continue
        head, _, params = line.partition("(")
        methods[head] = params.rstrip(")")
    return methods


def cap(lines: list[str], limit: int) -> str:
    if not lines:
        return "none"
    shown = lines[:limit]
    if len(lines) > limit:
        shown.append(f"... ({len(lines) - limit} more)")
    return "\n".join(shown)


def lens_facts(old: Source, new: Source) -> Section:
    counts, lines = diff_maps(flatten(old.facts), flatten(new.facts))
    return Section("Stock facts (StockFacts.exe)", counts, cap(lines, 10_000))


def lens_census(old: Source, new: Source) -> Section:
    texts = []
    for src in (old, new):
        proc = run(["mono", str(BIN / "Census.exe"), str(src.path)])
        if proc.returncode != 0:
            return Section(
                "Census (Census.exe)", {}, "", note=proc.stderr.strip() or "census failed"
            )
        texts.append(proc.stdout)
    counts, lines = diff_maps(parse_pairs(texts[0]), parse_pairs(texts[1]))
    return Section("Census (Census.exe)", counts, cap(lines, 10_000))


def list_surface(tool: str, dll: Path, tmp: Path, name: str) -> str:
    out = tmp / f"{name}.tsv"
    proc = run(["mono", str(BIN / tool), str(dll), str(out)])
    if proc.returncode != 0 or not out.is_file():
        raise RuntimeError(f"{tool} failed on {dll}: {proc.stderr.strip() or proc.stdout}")
    return out.read_text(encoding="utf-8", errors="replace")


def parse_surface_rows(text: str) -> dict[str, str]:
    """FullSurface `surface-types.md` rows: type name -> the rest of the row."""
    rows: dict[str, str] = {}
    for line in text.splitlines():
        if not line.startswith("| ") or line.startswith(("| Type", "|---")):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 7:
            continue
        rows[cells[0]] = " | ".join(cells[1:])
    return rows


def surface_rows(dll: Path, out_dir: Path) -> dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    proc = run(["mono", str(BIN / "FullSurface.exe"), str(dll), str(out_dir)])
    report = out_dir / "surface-types.md"
    if proc.returncode != 0 or not report.is_file():
        raise RuntimeError(f"FullSurface.exe failed on {dll}: {proc.stderr.strip() or proc.stdout}")
    return parse_surface_rows(report.read_text(encoding="utf-8", errors="replace"))


def lens_metadata(old: Source, new: Source, tmp: Path, limit: int) -> Section:
    """Per-type metadata drift: added/removed types and changed kind/base/counts."""
    title = "Type metadata (FullSurface.exe)"
    try:
        before = surface_rows(old.path, tmp / "surface_old")
        after = surface_rows(new.path, tmp / "surface_new")
    except RuntimeError as exc:
        return Section(title, {}, "", note=str(exc))
    counts, lines = diff_maps(before, after)
    return Section(title, counts, cap(lines, limit))


def lens_methods(old: Source, new: Source, tmp: Path, limit: int) -> Section:
    try:
        before = parse_methods(list_surface("MethodList.exe", old.path, tmp, "methods_old"))
        after = parse_methods(list_surface("MethodList.exe", new.path, tmp, "methods_new"))
    except RuntimeError as exc:
        return Section("Method signatures (MethodList.exe)", {}, "", note=str(exc))
    counts, lines = diff_maps(before, after)
    return Section("Method signatures (MethodList.exe)", counts, cap(lines, limit))


def lens_enums(old: Source, new: Source, tmp: Path, limit: int) -> Section:
    try:
        before = parse_pairs(list_surface("EnumList.exe", old.path, tmp, "enums_old"))
        after = parse_pairs(list_surface("EnumList.exe", new.path, tmp, "enums_new"))
    except RuntimeError as exc:
        return Section("Enum members (EnumList.exe)", {}, "", note=str(exc))
    counts, lines = diff_maps(before, after)
    return Section("Enum members (EnumList.exe)", counts, cap(lines, limit))


def lens_bodies(old: Source, new: Source, limit: int) -> Section:
    script = TOOLS / "asm_body_diff.py"
    proc = run([sys.executable, str(script), str(old.path), str(new.path)])
    if proc.returncode != 0:
        return Section("Method bodies (asm_body_diff.py)", {}, "", note=proc.stderr.strip())
    added = removed = changed = 0
    lines: list[str] = []
    for line in proc.stdout.splitlines():
        match = BODY_SUMMARY_RE.search(line)
        if match:
            _, _, added, removed, changed = (int(g) for g in match.groups())
            lines.append(line)
            continue
        if line.startswith((" + ", " - ", " ~ ")):
            lines.append(line)
    counts = {"added": added, "removed": removed, "changed": changed}
    return Section("Method bodies (asm_body_diff.py)", counts, cap(lines, limit))


def lens_parity(old_json: Path | None, new_json: Path | None, limit: int) -> Section:
    title = "Wire parity (parity_diff.py)"
    if old_json is None or new_json is None:
        return Section(title, {}, "", note="not measured: pass --parity-old and --parity-new")
    script = TOOLS / "parity" / "parity_diff.py"
    proc = run([sys.executable, str(script), str(old_json), str(new_json)])
    counts = {"changed": 1} if proc.returncode == 1 else {}
    body = cap(proc.stdout.splitlines(), limit)
    note = None if proc.returncode in (0, 1) else proc.stderr.strip() or f"rc={proc.returncode}"
    return Section(title, counts, body, note=note)


def lens_depot(old_path: Path | None, new_path: Path | None, limit: int) -> Section:
    """Non-managed content delta from Steam's own depot manifests."""
    title = "Depot manifest (steam_manifest.py)"
    if old_path is None or new_path is None:
        return Section(
            title,
            {},
            "",
            note="not measured: pass --steam-manifest-old and --steam-manifest-new",
        )
    old = read_manifest(old_path)
    new = read_manifest(new_path)
    if old.depot != new.depot:
        return Section(
            title,
            {},
            "",
            note=f"not measured: depot {old.depot} != {new.depot}",
        )
    counts, lines = diff_manifests(old, new, None)
    return Section(title, counts, cap([f"gid {old.gid} -> {new.gid}", *lines], limit))


def run_lenses(jobs: int, builders: list[Callable[[], Section]]) -> list[Section]:
    """Run the independent lenses, optionally concurrently (order is preserved).

    Every lens only reads the two DLLs and its own outputs, so overlapping them
    is safe; `jobs=1` is the reference path and must produce an identical report.
    """
    if jobs <= 1 or len(builders) < 2:
        return [build() for build in builders]
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        return list(pool.map(lambda build: build(), builders))


def section_markdown(index: int, section: Section) -> str:
    total = sum(section.counts.values())
    verdict = f"{total} change(s)" if total else "no change"
    lines = [f"## {index}. {section.title}", ""]
    if section.note:
        lines += [section.note, ""]
    if section.counts:
        detail = ", ".join(f"{k} {v}" for k, v in sorted(section.counts.items()))
        lines += [f"{verdict} ({detail})", ""]
    elif not section.note:
        lines += [verdict, ""]
    if section.body:
        lines += ["```", section.body, "```", ""]
    return "\n".join(lines)


def provenance_cell(source: Source) -> str:
    if source.depot_sha1 is None:
        return "not checked"
    verdict = "matches the local file" if source.depot_matches else "MISMATCHES the local file"
    return f"`{source.depot_sha1}` ({verdict})"


def report_markdown(
    old: Source, new: Source, sections: list[Section], generated: str, argv: list[str]
) -> str:
    drift = any(sum(s.counts.values()) for s in sections)
    per_lens = ", ".join(
        f"{s.title.split(' (')[0].lower()} {sum(s.counts.values())}" for s in sections
    )
    head = [
        f"# Build diff: {old.label} -> {new.label}",
        "",
        f"Generated {generated} by `tools/research_diff.py`.",
        "",
        "## Source identity",
        "",
        "| | old | new |",
        "|---|---|---|",
        f"| label | {old.label} | {new.label} |",
        f"| file | `{old.path}` | `{new.path}` |",
        f"| sha256 | `{old.sha256}` | `{new.sha256}` |",
        f"| bytes | {old.size} | {new.size} |",
        f"| version | {old.version} | {new.version} |",
        f"| stock wire | {old.wire} | {new.wire} |",
        f"| Steam build | {old.buildid or 'unknown'} | {new.buildid or 'unknown'} |",
        f"| depot manifest | {old.depot or 'not given'} | {new.depot or 'not given'} |",
        f"| depot file SHA-1 | {provenance_cell(old)} | {provenance_cell(new)} |",
        "",
        "## Verdict",
        "",
        f"drift: {'yes' if drift else 'no'} ({per_lens})",
        "",
        "## Reproduce",
        "",
        "```bash",
        " ".join(["python3", "tools/research_diff.py", *argv]),
        "```",
        "",
        "",
    ]
    return "\n".join(head) + "\n".join(
        section_markdown(i, section) for i, section in enumerate(sections, start=1)
    )


def candidate_dlls(game_dir: Path) -> list[Path]:
    """Assembly-CSharp.dll plus its retained backups (the tiny experiment files are not DLLs)."""
    names = ["Assembly-CSharp.dll", *sorted(p.name for p in game_dir.glob("Assembly-CSharp.dll.*"))]
    return [
        path
        for name in names
        if (path := game_dir / name).is_file() and path.stat().st_size > 1_000_000
    ]


def label_matches(label: str, facts: dict[str, Any]) -> bool:
    """Does a version label (`b9`, `V 3.2.0`, `V3.2.0 b9`) name this build?"""
    version = facts.get("version", {}) if isinstance(facts.get("version"), dict) else {}
    wanted = label.strip().lower()
    if not wanted:
        return False
    candidates = {
        f"b{version.get('build')}",
        str(version.get("display", "")).lower().replace(" ", ""),
        str(version.get("stock_wire", "")).lower().replace(" ", ""),
    }
    return wanted.replace(" ", "") in candidates


def resolve_pair(
    pair: str, game_dir: Path, steam_root: str | None, tmp: Path, pins: dict[str, Any]
) -> tuple[Source, Source, Path | None, Path | None, Path | None, Path | None]:
    """Resolve a label pair to DLLs, cached depot manifests and committed parity snapshots.

    A label is either a version (`b9`, `V3.2.0 b9`), matched on the facts each DLL
    reports, or a Steam build id (`24911252`), resolved through that build's cached
    depot manifest SHA-1. The cached depot
    manifest is then matched by the DLL's own SHA-1 as recorded in Steam's
    manifest, so all three artifacts provably belong to the same build.
    """
    if ":" not in pair:
        raise SourceError(f"--pair wants OLD:NEW, got {pair!r}")
    old_label, new_label = (part.strip() for part in pair.split(":", 1))
    candidates = candidate_dlls(game_dir)
    if not candidates:
        raise SourceError(f"no Assembly-CSharp.dll (or .dll.* backup) in {game_dir}")

    roots = roots_from(steam_root)
    cached = sorted(cached_manifests(DEFAULT_DEPOT, roots).values())
    buildids = pins_buildids(STEAM_PINS) | steam_log_buildids(DEFAULT_DEPOT, roots)
    gid_of_build = {build: gid for gid, build in buildids.items()}

    def depot_sha1(gid: str) -> str | None:
        manifest_path = manifest_for_gid(DEFAULT_DEPOT, gid, roots)
        return assembly_sha1(read_manifest(manifest_path)) if manifest_path else None

    resolved: dict[str, Source] = {}
    for label in (old_label, new_label):
        # A version label (`b9`, `V3.2.0 b9`) matches on the facts a DLL reports.
        for path in candidates:
            source = load_source(path, label, None, tmp, f"probe_{path.name}", pins)
            if label_matches(label, source.facts):
                resolved[label] = source
                break
        if label in resolved:
            continue
        # Otherwise a Steam build id resolves through its depot manifest's SHA-1.
        wanted = gid_of_build.get(label)
        expected = depot_sha1(wanted) if wanted else None
        for path in candidates:
            if expected is not None and sha1_file(path) == expected:
                resolved[label] = load_source(path, label, wanted, tmp, f"probe_{path.name}", pins)
                break
        if label not in resolved:
            found = ", ".join(p.name for p in candidates)
            known = ", ".join(sorted(buildids.values())) or "none known"
            raise SourceError(
                f"no DLL in {game_dir} matches {label!r} (candidates: {found}; "
                f"known build ids: {known})"
            )
    manifests: list[Path | None] = []
    for label in (old_label, new_label):
        source = resolved[label]
        local_sha1 = sha1_file(source.path)
        match = next(
            (
                manifest_path
                for manifest_path in cached
                if assembly_sha1(read_manifest(manifest_path)) == local_sha1
            ),
            None,
        )
        if match is not None:
            gid = match.name.split("_", 1)[1].split(".")[0]
            if gid in buildids:
                # The matched manifest names the build, so the report can label the
                # DLL with its Steam build id even when nothing else knows it.
                source = replace(source, buildid=buildids[gid])
                resolved[label] = source
        print(
            f"pair: {label} -> {source.path.name} sha256 {source.sha256[:12]} "
            f"build {source.buildid or 'unknown'}; manifest {match.name if match else 'not cached'}"
        )
        manifests.append(match)

    parity: list[Path | None] = []
    for label in (old_label, new_label):
        # Snapshots are named by version label; a build-id pair falls back to the
        # resolved DLL's own version (`parity_b9.json`).
        names = [f"parity_{label}.json"]
        version = resolved[label].facts.get("version")
        if isinstance(version, dict) and version.get("build") is not None:
            names.append(f"parity_b{version['build']}.json")
        parity.append(
            next(
                (
                    candidate
                    for name in names
                    if (candidate := DEFAULT_OUT_DIR.parent / "parity" / name).is_file()
                ),
                None,
            )
        )
    return (
        resolved[old_label],
        resolved[new_label],
        manifests[0],
        manifests[1],
        parity[0],
        parity[1],
    )


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="research_diff.py",
        description="Build-to-build research diff report across the maintained lenses.",
    )
    ap.add_argument("--old", default=None, help="baseline Assembly-CSharp.dll")
    ap.add_argument("--new", default=None, help="candidate Assembly-CSharp.dll")
    ap.add_argument(
        "--pair",
        default=None,
        metavar="OLD:NEW",
        help="resolve both DLLs, both cached depot manifests and both parity snapshots "
        "from their labels (e.g. b9:b10) instead of passing paths",
    )
    ap.add_argument(
        "--game-dir",
        default=None,
        help="Managed dir to scan for Assembly-CSharp.dll* candidates (default: the live install)",
    )
    ap.add_argument(
        "--steam-root",
        default=None,
        help="Steam root to scan for cached depot manifests (default: standard locations)",
    )
    ap.add_argument(
        "--label-old", default=None, help="baseline label (default: stock wire version)"
    )
    ap.add_argument(
        "--label-new", default=None, help="candidate label (default: stock wire version)"
    )
    ap.add_argument("--buildid-old", default=None, help="Steam build id for the baseline")
    ap.add_argument("--buildid-new", default=None, help="Steam build id for the candidate")
    ap.add_argument("--parity-old", default=None, help="baseline ParitySurface JSON snapshot")
    ap.add_argument("--parity-new", default=None, help="candidate ParitySurface JSON snapshot")
    ap.add_argument(
        "--steam-manifest-old",
        default=None,
        help="baseline cached depot manifest (<depot>_<gid>.manifest) for the content lens",
    )
    ap.add_argument(
        "--steam-manifest-new",
        default=None,
        help="candidate cached depot manifest for the content lens",
    )
    ap.add_argument(
        "--max-list", type=int, default=40, help="max detail lines per lens (default 40)"
    )
    ap.add_argument(
        "--out",
        default=None,
        help=f"report path, or - for stdout (default: {DEFAULT_OUT_DIR}/<old>-to-<new>-<date>.md)",
    )
    ap.add_argument(
        "--jobs",
        type=int,
        default=min(4, os.cpu_count() or 1),
        help="concurrent lenses (default: min(4, CPUs); 1 is the sequential reference)",
    )
    ap.add_argument("--json", action="store_true", help="emit the summary as JSON")
    ap.add_argument("--check", action="store_true", help="exit 1 when any lens reports drift")
    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    problem = prereq()
    if problem:
        print(f"research_diff: {problem}", file=sys.stderr)
        return 2
    if not args.pair and not (args.old and args.new):
        print("research_diff: pass --old/--new or --pair OLD:NEW", file=sys.stderr)
        return 2
    if args.pair and (args.old or args.new):
        print("research_diff: --pair and --old/--new are mutually exclusive", file=sys.stderr)
        return 2

    pins = load_steam_pins()
    parity_old = args.parity_old
    parity_new = args.parity_new
    manifest_old = args.steam_manifest_old
    manifest_new = args.steam_manifest_new
    label_old, label_new = args.label_old, args.label_new
    resolved_old = resolved_new = None
    if args.pair:
        live = _common.find_asm()
        game_dir = Path(args.game_dir) if args.game_dir else (live.parent if live else Path("."))
        try:
            with tempfile.TemporaryDirectory(
                prefix="research_diff_pair_", dir=_common.scratch_dir()
            ) as tmp_pair:
                (
                    resolved_old,
                    resolved_new,
                    manifest_old_path,
                    manifest_new_path,
                    parity_old_path,
                    parity_new_path,
                ) = resolve_pair(args.pair, game_dir, args.steam_root, Path(tmp_pair), pins)
        except (SourceError, ManifestError, RuntimeError) as exc:
            print(f"research_diff: {exc}", file=sys.stderr)
            return 2
        label_old = resolved_old.label
        label_new = resolved_new.label
        manifest_old = str(manifest_old_path) if manifest_old_path else None
        manifest_new = str(manifest_new_path) if manifest_new_path else None
        parity_old = str(parity_old_path) if parity_old_path else None
        parity_new = str(parity_new_path) if parity_new_path else None
        print(
            "pair: parity snapshots "
            + (
                f"{parity_old_path.name}, {parity_new_path.name}"
                if parity_old_path and parity_new_path
                else "not available (content/managed lenses still measured)"
            )
        )

    old_path = Path(args.old) if args.old else Path(resolved_old.path if resolved_old else "")
    new_path = Path(args.new) if args.new else Path(resolved_new.path if resolved_new else "")
    for path in (old_path, new_path):
        if not path.is_file():
            print(f"research_diff: dll not found: {path}", file=sys.stderr)
            return 2
    try:
        with tempfile.TemporaryDirectory(prefix="research_diff_", dir=_common.scratch_dir()) as tmp:
            tmp_path = Path(tmp)
            # --pair already resolved facts, labels and build ids; reloading would
            # throw the manifest-derived build id away.
            old = (
                replace(resolved_old, buildid=args.buildid_old)
                if resolved_old is not None and args.buildid_old
                else resolved_old
                or load_source(old_path, label_old, args.buildid_old, tmp_path, "old", pins)
            )
            new = (
                replace(resolved_new, buildid=args.buildid_new)
                if resolved_new is not None and args.buildid_new
                else resolved_new
                or load_source(new_path, label_new, args.buildid_new, tmp_path, "new", pins)
            )
            limit = max(0, args.max_list)
            provenance = [
                depot_provenance(source.path, Path(manifest) if manifest else None)
                for source, manifest in ((old, manifest_old), (new, manifest_new))
            ]
            if provenance[0] or provenance[1]:
                old = replace(
                    old,
                    depot=provenance[0][0] if provenance[0] else None,
                    depot_sha1=provenance[0][1] if provenance[0] else None,
                    depot_matches=provenance[0][2] if provenance[0] else None,
                )
                new = replace(
                    new,
                    depot=provenance[1][0] if provenance[1] else None,
                    depot_sha1=provenance[1][1] if provenance[1] else None,
                    depot_matches=provenance[1][2] if provenance[1] else None,
                )
                for side, source in (("old", old), ("new", new)):
                    if source.depot_sha1 and not source.depot_matches:
                        print(
                            f"research_diff: WARNING {side} DLL {source.path.name} does not match "
                            f"{source.depot} SHA-1 (not the bytes that manifest shipped)",
                            file=sys.stderr,
                        )

            builders: list[Callable[[], Section]] = [
                partial(lens_facts, old, new),
                partial(lens_census, old, new),
                partial(lens_metadata, old, new, tmp_path, limit),
                partial(lens_methods, old, new, tmp_path, limit),
                partial(lens_enums, old, new, tmp_path, limit),
                partial(lens_bodies, old, new, limit),
                partial(
                    lens_parity,
                    Path(parity_old) if parity_old else None,
                    Path(parity_new) if parity_new else None,
                    limit,
                ),
                partial(
                    lens_depot,
                    Path(manifest_old) if manifest_old else None,
                    Path(manifest_new) if manifest_new else None,
                    limit,
                ),
            ]
            sections = run_lenses(max(1, args.jobs), builders)
    except (RuntimeError, ManifestError, subprocess.TimeoutExpired) as exc:
        print(f"research_diff: {exc}", file=sys.stderr)
        return 2

    generated = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    date = generated[:10].replace("-", "")
    # The reproduce line must be the command a reader should run: no output
    # redirection and no summary flag.
    argv_tail: list[str] = []
    skip_value = False
    for arg in argv if argv is not None else sys.argv[1:]:
        if skip_value:
            skip_value = False
            continue
        if arg in {"--json", "--out", "--jobs"} or arg.startswith(("--out=", "--jobs=")):
            skip_value = arg in {"--out", "--jobs"}
            continue
        argv_tail.append(arg)
    text = report_markdown(old, new, sections, generated, argv_tail)

    drift = any(sum(s.counts.values()) for s in sections)
    if args.out == "-":
        sys.stdout.write(text)
    else:
        out = (
            Path(args.out)
            if args.out
            else DEFAULT_OUT_DIR / f"{old.label}-to-{new.label}-{date}.md"
        )
        out.parent.mkdir(parents=True, exist_ok=True)
        staging = out.with_name(f".{out.name}.tmp{os.getpid()}")
        staging.write_text(text, encoding="utf-8")
        staging.replace(out)
        print(f"research_diff: wrote {out} (drift: {'yes' if drift else 'no'})")

    if args.json:
        payload = {
            "old": {"label": old.label, "sha256": old.sha256, "buildid": old.buildid},
            "new": {"label": new.label, "sha256": new.sha256, "buildid": new.buildid},
            "drift": drift,
            "lenses": {s.title: s.counts for s in sections},
        }
        print(json.dumps(payload, indent=2))

    return 1 if (args.check and drift) else 0


if __name__ == "__main__":
    sys.exit(main())
