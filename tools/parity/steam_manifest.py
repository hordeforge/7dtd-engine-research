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
import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

MAGIC = 0x71F617D0
DEFAULT_DEPOT = "294422"  # dedicated-server content depot
STEAM_ROOTS = (
    Path.home() / ".local/share/Steam",
    Path.home() / ".steam/steam",
    Path.home() / ".steam/root",
    Path.home() / ".local/share/Steam/steamapps",
)
HASH_CHUNK = 1 << 20


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


def find_manifest(depot: str, roots: tuple[Path, ...] = STEAM_ROOTS) -> Path | None:
    """Newest cached manifest for a depot, or None."""
    candidates: list[Path] = []
    for root in roots:
        for sub in ("depotcache", "steamapps/depotcache"):
            candidates.extend((root / sub).glob(f"{depot}_*.manifest"))
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def sha1_file(path: Path) -> str:
    digest = hashlib.sha1()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(HASH_CHUNK), b""):
            digest.update(chunk)
    return digest.hexdigest()


def match_entries(manifest: Manifest, needle: str) -> list[Entry]:
    lowered = needle.lower().replace("/", "\\")
    return [e for e in manifest.entries if lowered in e.name.lower()]


def verify(manifest: Manifest, root: Path, only: str | None) -> tuple[int, int, int, list[str]]:
    ok = missing = bad = 0
    problems: list[str] = []
    for entry in manifest.entries:
        if not entry.sha1 or entry.size == 0:
            continue  # directory, empty file, or symlink: nothing to hash
        if only and only.lower().replace("/", "\\") not in entry.name.lower():
            continue
        local = root / entry.name.replace("\\", "/")
        if not local.is_file():
            missing += 1
            problems.append(f"MISSING {entry.name}")
            continue
        if local.stat().st_size != entry.size:
            bad += 1
            problems.append(f"SIZE {entry.name}: {local.stat().st_size} != {entry.size}")
            continue
        if sha1_file(local) != entry.sha1:
            bad += 1
            problems.append(f"SHA1 {entry.name}: local file differs from the depot manifest")
            continue
        ok += 1
    return ok, missing, bad, problems


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


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="steam_manifest.py",
        description="Read Steam's cached depot manifest (per-file SHA-1, offline).",
    )
    ap.add_argument("--manifest", default=None, help="explicit <depot>_<gid>.manifest path")
    ap.add_argument("--depot", default=DEFAULT_DEPOT, help=f"depot id (default {DEFAULT_DEPOT})")
    ap.add_argument("--list", action="store_true", help="list every entry")
    ap.add_argument("--find", default=None, metavar="SUBSTR", help="entries whose path matches")
    ap.add_argument("--verify", default=None, metavar="DIR", help="hash DIR against the manifest")
    ap.add_argument(
        "--diff",
        default=None,
        metavar="OLD.manifest",
        help="compare the selected manifest (new) against this older one",
    )
    ap.add_argument("--only", default=None, metavar="SUBSTR", help="limit --verify/--list/--diff")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    path = Path(args.manifest) if args.manifest else find_manifest(args.depot)
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
            older = read_manifest(Path(args.diff))
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
            payload |= {
                "old_manifest": str(older.path),
                "old_gid": older.gid,
                "changes": counts,
                "lines": lines,
            }
        elif args.verify:
            ok, missing, bad, problems = verify(manifest, Path(args.verify), args.only)
            payload |= {"ok": ok, "missing": missing, "mismatch": bad, "problems": problems[:200]}
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
        print(
            f"diff: {counts['added']} added, {counts['removed']} removed, "
            f"{counts['changed']} changed ({older.gid} -> {manifest.gid})"
        )
        return 0

    if args.verify:
        ok, missing, bad, problems = verify(manifest, Path(args.verify), args.only)
        for line in problems[:40]:
            print(line, file=sys.stderr)
        if len(problems) > 40:
            print(f"... ({len(problems) - 40} more)", file=sys.stderr)
        print(f"verify: {ok} ok, {missing} missing, {bad} mismatch (root {args.verify})")
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
