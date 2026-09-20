#!/usr/bin/env python3
"""Build-to-build research diff report.

One command that compares two stock `Assembly-CSharp.dll` builds through every
cheap lens this corpus already has, then writes a single build-stamped Markdown
report: source identity (size + sha256 + version), a drift verdict, and the
per-lens detail. The lenses are the maintained tools, not reimplementations:

  facts    StockFacts.exe      version/sim/network/save/behaviour fields
  census   Census.exe          whole-assembly type/method/IL counts
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
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent / "tests"))
sys.path.insert(0, str(Path(__file__).resolve().parent / "parity"))
import _common
from steam_manifest import ManifestError, diff_manifests, read_manifest

TOOLS = _common.TOOLS
REPO = _common.REPO
BIN = _common.BIN
DEFAULT_OUT_DIR = REPO / "workspace" / "outputs" / "diffs"
STEAM_PINS = TOOLS / "data" / "steam_builds.json"

FACTS_SKIP = {"asm", "extracted_utc"}
BODY_SUMMARY_RE = re.compile(
    r"methods bak=(\d+) live=(\d+) added=(\d+) removed=(\d+) body-changed=(\d+)"
)


@dataclass(frozen=True)
class Source:
    label: str
    path: Path
    sha256: str
    size: int
    facts: dict[str, Any]
    buildid: str | None

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
        for name in ("StockFacts.exe", "Census.exe", "MethodList.exe", "EnumList.exe")
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


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="research_diff.py",
        description="Build-to-build research diff report across the maintained lenses.",
    )
    ap.add_argument("--old", required=True, help="baseline Assembly-CSharp.dll")
    ap.add_argument("--new", required=True, help="candidate Assembly-CSharp.dll")
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
    ap.add_argument("--json", action="store_true", help="emit the summary as JSON")
    ap.add_argument("--check", action="store_true", help="exit 1 when any lens reports drift")
    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    problem = prereq()
    if problem:
        print(f"research_diff: {problem}", file=sys.stderr)
        return 2
    old_path, new_path = Path(args.old), Path(args.new)
    for path in (old_path, new_path):
        if not path.is_file():
            print(f"research_diff: dll not found: {path}", file=sys.stderr)
            return 2

    pins = load_steam_pins()
    try:
        with tempfile.TemporaryDirectory(prefix="research_diff_", dir=_common.scratch_dir()) as tmp:
            tmp_path = Path(tmp)
            old = load_source(old_path, args.label_old, args.buildid_old, tmp_path, "old", pins)
            new = load_source(new_path, args.label_new, args.buildid_new, tmp_path, "new", pins)
            limit = max(0, args.max_list)
            sections = [
                lens_facts(old, new),
                lens_census(old, new),
                lens_methods(old, new, tmp_path, limit),
                lens_enums(old, new, tmp_path, limit),
                lens_bodies(old, new, limit),
                lens_parity(
                    Path(args.parity_old) if args.parity_old else None,
                    Path(args.parity_new) if args.parity_new else None,
                    limit,
                ),
                lens_depot(
                    Path(args.steam_manifest_old) if args.steam_manifest_old else None,
                    Path(args.steam_manifest_new) if args.steam_manifest_new else None,
                    limit,
                ),
            ]
    except (RuntimeError, ManifestError, subprocess.TimeoutExpired) as exc:
        print(f"research_diff: {exc}", file=sys.stderr)
        return 2

    generated = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    date = generated[:10].replace("-", "")
    argv_tail = [a for a in (argv if argv is not None else sys.argv[1:]) if a != "--json"]
    text = report_markdown(old, new, sections, generated, argv_tail)

    drift = any(sum(s.counts.values()) for s in sections)
    if args.out == "-":
        print(text)
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
