#!/usr/bin/env python3
"""Steam's own depot manifest: per-file checksums, offline.

The Steam client caches the depot manifest it installed from at
`<steam>/depotcache/<depot>_<manifest-gid>.manifest`. For the 7DTD dedicated
depot (294422) that file is **plaintext** protobuf (magic 0x71F617D0), so
Steam's published checksums are readable with no steamcmd, no login, and no
network: one entry per file with size, flags, whole-file SHA-1 and per-chunk
SHA-1s. That is the checksum source SteamDB cannot give us (it 403s scripted
clients and has no public API).

  steam_manifest.py                          # summary of the newest 294422 manifest
  steam_manifest.py --find Assembly-CSharp    # size + SHA-1 for matching entries
  steam_manifest.py --verify <install-dir> --only Managed
                                             # hash local files against Steam's SHA-1s
  steam_manifest.py --list --json             # machine-readable full file list
  steam_manifest.py --manifest <file>         # a specific cached manifest (e.g. an old build)

`--verify` hashes only files present locally and reports missing/mismatched
paths; exit 1 when any disagree. A full-install verify reads every byte (about
17 GB here), so use `--only` while iterating.

Exit codes: 0 ok, 1 verify mismatch, 2 unusable input.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

MAGIC = 0x71F617D0
DEFAULT_DEPOT = "294422"  # dedicated-server content depot
PINS = Path(__file__).resolve().parent.parent / "data" / "steam_builds.json"
STEAM_ROOTS = (
    Path.home() / ".local/share/Steam",
    Path.home() / ".steam/steam",
    Path.home() / ".steam/root",
    Path.home() / ".local/share/Steam/steamapps",
)
HASH_CHUNK = 1 << 20
# Files the running game rewrites from its own settings. A mismatch here is
# expected on an install that has been launched; the hint explains it rather than
# hiding it, and `--ignore` excludes it explicitly when the rest matters.
RUNTIME_WRITTEN = {
    "platform.cfg": "the dedicated server rewrites this from its platform settings",
}
LOG_RE = re.compile(r"BuildID (\d+)\)[^:]*: (\d+) \((\d+)\)")


class ManifestError(Exception):
    """The manifest file could not be read."""


@dataclass(frozen=True)
class Entry:
    name: str
    size: int
    flags: int
    sha1: str | None
    chunks: int


@dataclass(frozen=True)
class Manifest:
    path: Path
    gid: str
    entries: list[Entry]
    trailer: int = 0

    @property
    def depot(self) -> str:
        return self.path.name.split("_", 1)[0]


def _varint(data: bytes, offset: int) -> tuple[int, int]:
    value = 0
    shift = 0
    while True:
        if offset >= len(data):
            raise ManifestError("truncated varint")
        byte = data[offset]
        offset += 1
        value |= (byte & 0x7F) << shift
        shift += 7
        if not byte & 0x80:
            return value, offset


def _fields(block: bytes) -> Iterator[tuple[int, int, Any]]:
    offset = 0
    while offset < len(block):
        key, offset = _varint(block, offset)
        field, wire = key >> 3, key & 7
        value: Any
        if wire == 0:
            value, offset = _varint(block, offset)
        elif wire == 2:
            length, offset = _varint(block, offset)
            if offset + length > len(block):
                raise ManifestError("truncated length-delimited field")
            value = block[offset : offset + length]
            offset += length
        elif wire == 5:
            value = struct.unpack_from("<I", block, offset)[0]
            offset += 4
        elif wire == 1:
            value = struct.unpack_from("<Q", block, offset)[0]
            offset += 8
        else:
            raise ManifestError(f"unsupported wire type {wire}")
        yield field, wire, value


def _entry(block: bytes) -> Entry:
    name = ""
    size = 0
    flags = 0
    sha1: str | None = None
    chunks = 0
    for field, wire, value in _fields(block):
        if field == 1 and wire == 2:
            name = bytes(value).decode("utf-8", "replace")
        elif field == 2 and wire == 0:
            size = int(value)
        elif field == 3 and wire == 0:
            flags = int(value)
        elif field == 5 and wire == 2 and len(value) == 20:
            sha1 = bytes(value).hex()
        elif field == 6 and wire == 2:
            chunks += 1
    return Entry(name=name, size=size, flags=flags, sha1=sha1, chunks=chunks)


def read_manifest(path: Path) -> Manifest:
    """Parse the entry table: magic(4) + entry-table byte length(4) + entries, then a trailer.

    The 70-byte trailer that follows the entry table is per-manifest metadata
    that does not parse as protobuf at any offset tried; it is counted and left
    opaque (the depot id and manifest gid already come from the file name).
    """
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise ManifestError(f"unreadable manifest {path}: {exc}") from exc
    if len(data) < 8 or struct.unpack_from("<I", data, 0)[0] != MAGIC:
        raise ManifestError(f"{path}: not a Steam depot manifest (bad magic)")
    gid = path.name.split("_", 1)[1].split(".")[0] if "_" in path.name else "unknown"
    entries: list[Entry] = []
    table_end = 8 + struct.unpack_from("<I", data, 4)[0]
    if table_end > len(data):
        raise ManifestError(f"{path}: entry table length {table_end} exceeds file size {len(data)}")
    offset = 8
    while offset < table_end:
        key, offset = _varint(data, offset)
        field, wire = key >> 3, key & 7
        if field != 1 or wire != 2:
            raise ManifestError(f"{path}: unexpected top-level field {field}/wire {wire}")
        length, offset = _varint(data, offset)
        if offset + length > table_end:
            raise ManifestError(f"{path}: truncated entry at offset {offset}")
        entries.append(_entry(data[offset : offset + length]))
        offset += length
    if not entries:
        raise ManifestError(f"{path}: no file entries")
    return Manifest(path=path, gid=gid, entries=entries, trailer=len(data) - table_end)


def roots_from(value: str | None) -> tuple[Path, ...]:
    """Explicit --steam-root wins; otherwise the standard Steam locations."""
    return (Path(value).expanduser(),) if value else STEAM_ROOTS


def cached_manifests(depot: str, roots: tuple[Path, ...] = STEAM_ROOTS) -> dict[str, Path]:
    """gid -> manifest path for every manifest of this depot on disk."""
    found: dict[str, Path] = {}
    for root in roots:
        for sub in ("depotcache", "steamapps/depotcache"):
            for path in (root / sub).glob(f"{depot}_*.manifest"):
                gid = path.name.split("_", 1)[1].split(".")[0]
                best = found.get(gid)
                if best is None or path.stat().st_mtime > best.stat().st_mtime:
                    found[gid] = path
    return found


def steam_log_buildids(depot: str, roots: tuple[Path, ...] = STEAM_ROOTS) -> dict[str, str]:
    """gid -> Steam build id, paired from the client's own content log.

    Steam writes `finished update, N mounted depots (BuildID <id>) : <depot>
    (<gid>)` on every install, which is the only local source that pairs a
    manifest with the build id that shipped it.
    """
    mapping: dict[str, str] = {}
    for root in roots:
        log = root / "logs" / "content_log.txt"
        try:
            text = log.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for match in LOG_RE.finditer(text):
            if match.group(2) == depot:
                mapping[match.group(3)] = match.group(1)
    return mapping


def pins_buildids(path: Path) -> dict[str, str]:
    """gid -> build id from the committed pin file (studied build + history).

    The client's content log rotates; the pin file keeps the build ids of
    earlier studied builds so an old cached manifest stays labelled.
    """
    try:
        data: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(data, dict):
        return {}
    mapping: dict[str, str] = {}
    studied = data.get("studied")
    if isinstance(studied, dict) and studied.get("manifest") and studied.get("buildid"):
        mapping[str(studied["manifest"])] = str(studied["buildid"])
    history = data.get("history")
    for entry in history if isinstance(history, list) else []:
        if isinstance(entry, dict) and entry.get("gid") and entry.get("buildid"):
            mapping[str(entry["gid"])] = str(entry["buildid"])
    return mapping


def find_manifest(depot: str, roots: tuple[Path, ...] = STEAM_ROOTS) -> Path | None:
    """Newest cached manifest for a depot, or None."""
    candidates = cached_manifests(depot, roots)
    if not candidates:
        return None
    return max(candidates.values(), key=lambda p: p.stat().st_mtime)


def resolve_manifest_arg(
    value: str,
    depot: str,
    roots: tuple[Path, ...],
    pins: dict[str, str] | None = None,
) -> Path:
    """A manifest path, a manifest gid, or a Steam build id -> the cached file.

    `--history` prints the gids and build ids, so accepting them here removes the
    need to paste a `~/.local/share/Steam/depotcache/...` path for every diff.
    """
    direct = Path(value).expanduser()
    if direct.is_file():
        return direct
    cached = cached_manifests(depot, roots)
    wanted = value.strip()
    if wanted in cached:
        return cached[wanted]
    buildids = (pins if pins is not None else pins_buildids(PINS)) | steam_log_buildids(
        depot, roots
    )
    for gid, build in buildids.items():
        if build == wanted and gid in cached:
            return cached[gid]
    known = ", ".join(sorted(cached)) or "none cached"
    raise ManifestError(
        f"{value!r} is neither a file nor a cached manifest gid/build id for depot {depot} "
        f"(cached gids: {known})"
    )


def sha1_file(path: Path) -> str:
    digest = hashlib.sha1()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(HASH_CHUNK), b""):
            digest.update(chunk)
    return digest.hexdigest()


def match_entries(manifest: Manifest, needle: str) -> list[Entry]:
    lowered = needle.lower().replace("/", "\\")
    return [e for e in manifest.entries if lowered in e.name.lower()]


GAME_ASSEMBLY = "managed/assembly-csharp.dll"


def assembly_entry(manifest: Manifest) -> Entry | None:
    """The depot entry for the managed game assembly, when it has a SHA-1."""
    return next(
        (entry for entry in match_entries(manifest, GAME_ASSEMBLY) if entry.sha1),
        None,
    )


def assembly_sha1(manifest: Manifest) -> str | None:
    entry = assembly_entry(manifest)
    return entry.sha1 if entry else None


def manifest_for_gid(depot: str, gid: str, roots: tuple[Path, ...] = STEAM_ROOTS) -> Path | None:
    """The cached manifest file with this gid, or None."""
    return next(
        (path for path in cached_manifests(depot, roots).values() if f"_{gid}." in path.name),
        None,
    )


def _runtime_hint(name: str) -> str:
    """A one-line explanation for a file the game is known to rewrite."""
    for path, why in RUNTIME_WRITTEN.items():
        if name.endswith(path):
            return f" (runtime-written: {why}; --ignore {path} to skip it)"
    return ""


def verify(
    manifest: Manifest, root: Path, only: str | None, ignore: tuple[str, ...] = ()
) -> tuple[int, int, int, list[str], int]:
    """Hash local files against Steam's manifest.

    `ignore` skips paths containing any of its substrings and reports how many
    were skipped: a file the running server rewrites (see platform.cfg in the
    methodology) should be excluded explicitly, never silently.
    """
    ok = missing = bad = ignored = 0
    problems: list[str] = []
    for entry in manifest.entries:
        if not entry.sha1 or entry.size == 0:
            continue  # directory, empty file, or symlink: nothing to hash
        lowered = entry.name.lower()
        if only and only.lower().replace("/", "\\") not in lowered:
            continue
        if any(pattern.lower() in lowered for pattern in ignore):
            ignored += 1
            continue
        local = root / entry.name.replace("\\", "/")
        if not local.is_file():
            missing += 1
            problems.append(f"MISSING {entry.name}")
            continue
        if local.stat().st_size != entry.size:
            bad += 1
            problems.append(
                f"SIZE {entry.name}: {local.stat().st_size} != {entry.size}"
                + _runtime_hint(entry.name)
            )
            continue
        if sha1_file(local) != entry.sha1:
            bad += 1
            problems.append(
                f"SHA1 {entry.name}: local file differs from the depot manifest"
                + _runtime_hint(entry.name)
            )
            continue
        ok += 1
    return ok, missing, bad, problems, ignored


def diff_manifests(
    old: Manifest, new: Manifest, only: str | None
) -> tuple[dict[str, int], list[str]]:
    """Per-file add/remove/change between two depot manifests (same depot)."""
    before = {e.name: e for e in old.entries}
    after = {e.name: e for e in new.entries}
    counts = {"added": 0, "removed": 0, "changed": 0}
    lines: list[str] = []
    for name in sorted(set(before) | set(after)):
        if only and only.lower().replace("/", "\\") not in name.lower():
            continue
        a, b = before.get(name), after.get(name)
        if a is None and b is not None:
            counts["added"] += 1
            lines.append(f"+ {b.size:>12} {b.sha1 or '-':40} {name}")
        elif b is None and a is not None:
            counts["removed"] += 1
            lines.append(f"- {a.size:>12} {a.sha1 or '-':40} {name}")
        elif a is not None and b is not None and (a.size != b.size or a.sha1 != b.sha1):
            counts["changed"] += 1
            lines.append(
                f"~ {name}: size {a.size} -> {b.size}; sha1 {a.sha1 or '-'} -> {b.sha1 or '-'}"
            )
    return counts, lines


def print_history(
    depot: str, roots: tuple[Path, ...], as_json: bool, pinned: dict[str, str] | None = None
) -> int:
    """Every cached manifest of the depot, newest first, with its build id."""
    cached = cached_manifests(depot, roots)
    if not cached:
        print(f"steam_manifest: no cached manifest for depot {depot}", file=sys.stderr)
        return 2
    buildids = (pinned or {}) | steam_log_buildids(depot, roots)
    rows: list[dict[str, Any]] = []
    for gid, path in cached.items():
        try:
            manifest = read_manifest(path)
            files = len(manifest.entries)
            size = sum(e.size for e in manifest.entries)
        except ManifestError as exc:
            print(f"steam_manifest: {exc}", file=sys.stderr)
            return 2
        rows.append(
            {
                "gid": gid,
                "buildid": buildids.get(gid),
                "files": files,
                "bytes": size,
                "cached_at": datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).strftime(
                    "%Y-%m-%d %H:%MZ"
                ),
                "path": str(path),
            }
        )
    rows.sort(key=lambda r: str(r["cached_at"]), reverse=True)
    if as_json:
        print(json.dumps({"depot": depot, "cached": rows}, indent=2))
        return 0
    print(f"depot: {depot}  cached manifests: {len(rows)}")
    print(f"{'gid':<21} {'buildid':<11} {'files':>6} {'bytes':>13}  cached_at")
    for row in rows:
        print(
            f"{row['gid']:<21} {row['buildid'] or '-':<11} {row['files']:>6} "
            f"{row['bytes']:>13}  {row['cached_at']}"
        )
    if len(rows) > 1:
        print(
            "diff them: steam_manifest.py --manifest <new.gid>.manifest --diff <old.gid>.manifest"
        )
    return 0


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="steam_manifest.py",
        description="Read Steam's cached depot manifest (per-file SHA-1, offline).",
    )
    ap.add_argument(
        "--manifest",
        default=None,
        help="manifest file, or a cached manifest gid / Steam build id (default: newest cached)",
    )
    ap.add_argument("--depot", default=DEFAULT_DEPOT, help=f"depot id (default {DEFAULT_DEPOT})")
    ap.add_argument("--list", action="store_true", help="list every entry")
    ap.add_argument("--find", default=None, metavar="SUBSTR", help="entries whose path matches")
    ap.add_argument("--verify", default=None, metavar="DIR", help="hash DIR against the manifest")
    ap.add_argument(
        "--diff",
        default=None,
        metavar="OLD",
        help="compare the selected manifest (new) against this older file, gid or build id",
    )
    ap.add_argument(
        "--history",
        action="store_true",
        help="list every cached manifest of the depot with its build id",
    )
    ap.add_argument(
        "--steam-root", default=None, help="Steam root to scan (default: standard locations)"
    )
    ap.add_argument("--pins", default=str(PINS), help=f"build-id pin file (default: {PINS})")
    ap.add_argument("--only", default=None, metavar="SUBSTR", help="limit --verify/--list/--diff")
    ap.add_argument(
        "--ignore",
        action="append",
        default=[],
        metavar="SUBSTR",
        help="skip manifest paths containing SUBSTR (repeatable; for files rewritten at runtime)",
    )
    ap.add_argument("--json", action="store_true", help="emit JSON")
    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    roots = roots_from(args.steam_root)
    pinned = pins_buildids(Path(args.pins))
    if args.history:
        return print_history(args.depot, roots, args.json, pinned)
    try:
        path = (
            resolve_manifest_arg(args.manifest, args.depot, roots)
            if args.manifest
            else find_manifest(args.depot, roots)
        )
    except ManifestError as exc:
        print(f"steam_manifest: {exc}", file=sys.stderr)
        return 2
    if path is None:
        print(f"steam_manifest: no cached manifest for depot {args.depot}", file=sys.stderr)
        return 2
    try:
        manifest = read_manifest(path)
    except ManifestError as exc:
        print(f"steam_manifest: {exc}", file=sys.stderr)
        return 2

    selected = match_entries(manifest, args.only) if args.only else manifest.entries

    older: Manifest | None = None
    if args.diff:
        try:
            older = read_manifest(resolve_manifest_arg(args.diff, args.depot, roots, pinned))
        except ManifestError as exc:
            print(f"steam_manifest: {exc}", file=sys.stderr)
            return 2
        if older.depot != manifest.depot:
            print(
                f"steam_manifest: refusing to diff depot {older.depot} against {manifest.depot}",
                file=sys.stderr,
            )
            return 2

    if args.json:
        payload: dict[str, Any] = {
            "manifest": str(manifest.path),
            "depot": manifest.depot,
            "gid": manifest.gid,
            "files": len(manifest.entries),
            "selected": len(selected),
            "trailer_bytes": manifest.trailer,
        }
        if older is not None:
            counts, lines = diff_manifests(older, manifest, args.only)
            buildids = pinned | steam_log_buildids(manifest.depot, roots)
            payload |= {
                "old_manifest": str(older.path),
                "old_gid": older.gid,
                "old_buildid": buildids.get(older.gid),
                "buildid": buildids.get(manifest.gid),
                "changes": counts,
                "lines": lines,
            }
        elif args.verify:
            ok, missing, bad, problems, ignored = verify(
                manifest, Path(args.verify), args.only, tuple(args.ignore)
            )
            payload |= {
                "ok": ok,
                "missing": missing,
                "mismatch": bad,
                "ignored": ignored,
                "problems": problems[:200],
            }
        elif args.find or args.list:
            payload["entries"] = [
                {
                    "name": e.name,
                    "size": e.size,
                    "flags": e.flags,
                    "sha1": e.sha1,
                    "chunks": e.chunks,
                }
                for e in (match_entries(manifest, args.find) if args.find else selected)
            ]
        print(json.dumps(payload, indent=2))
        return 0

    print(
        f"manifest: {manifest.path}\ndepot: {manifest.depot}  gid: {manifest.gid}  "
        f"files: {len(manifest.entries)}  chunks: {sum(e.chunks for e in manifest.entries)}  "
        f"trailer bytes: {manifest.trailer}"
    )

    if older is not None:
        counts, lines = diff_manifests(older, manifest, args.only)
        for line in lines:
            print(line)
        buildids = pinned | steam_log_buildids(manifest.depot, roots)
        old_label = f"build {buildids[older.gid]}" if older.gid in buildids else older.gid
        new_label = f"build {buildids[manifest.gid]}" if manifest.gid in buildids else manifest.gid
        print(
            f"diff: {counts['added']} added, {counts['removed']} removed, "
            f"{counts['changed']} changed ({old_label} -> {new_label})"
        )
        return 0

    if args.verify:
        ok, missing, bad, problems, ignored = verify(
            manifest, Path(args.verify), args.only, tuple(args.ignore)
        )
        for line in problems[:40]:
            print(line, file=sys.stderr)
        if len(problems) > 40:
            print(f"... ({len(problems) - 40} more)", file=sys.stderr)
        print(
            f"verify: {ok} ok, {missing} missing, {bad} mismatch"
            + (f", {ignored} ignored" if ignored else "")
            + f" (root {args.verify})"
        )
        return 1 if (missing or bad) else 0

    if args.find:
        for entry in match_entries(manifest, args.find):
            print(f"{entry.size:>12}  {entry.sha1 or '-':40}  {entry.name}")
        return 0

    if args.list:
        for entry in selected:
            print(f"{entry.size:>12}  {entry.sha1 or '-':40}  {entry.name}")
        return 0

    print(
        "hint: --find <substr> for one file's SHA-1, --verify <install-dir> [--only <substr>] "
        "to hash local files against Steam's checksums"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
