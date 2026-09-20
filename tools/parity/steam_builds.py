#!/usr/bin/env python3
"""Find the newest 7DTD dedicated-server build and pin the build we studied.

SteamDB has no public API and rate-limits/403s scripted clients, so the same
facts come from Steam's own app info (PICS mirror, app 294420): every branch's
build id and the depot 294422 manifest id. SteamDB pages stay useful by hand
(https://steamdb.info/app/294420/depots/); this tool is the machine path.

  steam_builds.py                    # branch table + installed build + next step
  steam_builds.py --json             # machine-readable snapshot
  steam_builds.py --check            # exit 1 when a newer build than the pin exists
  steam_builds.py --print-fetch --branch latest_experimental  # fetch by name if unlisted
  steam_builds.py --fetch            # download + snapshot the selected branch
  steam_builds.py --record           # pin the selected branch as the studied build

`tools/data/steam_builds.json` records which Steam build the studied
`Assembly-CSharp.dll` came from (build id + depot manifest + DLL sha256), so a
diff narrative can name its source build instead of "the local artifact".

Exit codes: 0 ok, 1 drift detected by --check, 2 unusable input/source.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PARITY = Path(__file__).resolve().parent
TOOLS = PARITY.parent
sys.path.insert(0, str(PARITY))
from steam_manifest import cached_manifests, roots_from, steam_log_buildids  # noqa: E402

PINS = TOOLS / "data" / "steam_builds.json"
STOCK_FACTS = TOOLS / "data" / "stock_facts.json"
FETCH = PARITY / "fetch_version.sh"

APP = "294420"
DEPOT = "294422"  # dedicated-server content depot (linux/windows payload)
PICS_URL = f"https://api.steamcmd.net/v1/info/{APP}"
DEFAULT_APPMANIFEST = Path.home() / ".local/share/Steam/steamapps" / f"appmanifest_{APP}.acf"
LABEL_RE = re.compile(r"^[A-Za-z0-9._-]+$")
_KV_RE = re.compile(r'^\s*"([^"]+)"\s+"([^"]*)"\s*$')
_DEPOT_RE = re.compile(r'^\s*"(\d+)"\s*$')


class SourceError(Exception):
    """The app-info payload or appmanifest could not be used."""


@dataclass(frozen=True)
class Branch:
    name: str
    buildid: str | None
    manifest: str | None
    download: int | None
    size: int | None
    updated: int | None
    description: str | None


@dataclass(frozen=True)
class Snapshot:
    source: str
    branches: list[Branch]


def _int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def parse_snapshot(appinfo: Any, source: str, app: str = APP, depot: str = DEPOT) -> Snapshot:
    """Pull branch build ids + depot manifests out of a PICS app-info payload."""
    try:
        depots = appinfo["data"][app]["depots"]
        raw_branches = depots["branches"]
        raw_manifests = depots[depot].get("manifests", {})
    except (KeyError, TypeError) as exc:
        raise SourceError(f"app info has no data.{app}.depots.{depot} branches: {exc!r}") from exc
    if not isinstance(raw_branches, dict) or not raw_branches:
        raise SourceError(f"app info has an empty branch table for app {app}")
    branches: list[Branch] = []
    for name, raw in raw_branches.items():
        raw = raw if isinstance(raw, dict) else {}
        manifest = raw_manifests.get(name)
        manifest = manifest if isinstance(manifest, dict) else {}
        branches.append(
            Branch(
                name=str(name),
                buildid=str(raw["buildid"]) if raw.get("buildid") else None,
                manifest=str(manifest["gid"]) if manifest.get("gid") else None,
                download=_int(manifest.get("download")),
                size=_int(manifest.get("size")),
                updated=_int(raw.get("timebuildupdated")),
                description=str(raw["description"]) if raw.get("description") else None,
            )
        )
    branches.sort(key=lambda b: (b.name != "public", -(b.updated or 0), b.name))
    return Snapshot(source=source, branches=branches)


def load_appinfo(path: Path) -> Snapshot:
    try:
        with path.open(encoding="utf-8") as fh:
            appinfo: Any = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        raise SourceError(f"unreadable app info {path}: {exc}") from exc
    return parse_snapshot(appinfo, f"file:{path}")


def fetch_appinfo(url: str = PICS_URL, timeout: float = 30.0) -> Snapshot:
    request = urllib.request.Request(url, headers={"User-Agent": "7dtd-engine-research"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            appinfo: Any = json.load(response)
    except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        raise SourceError(f"cannot read {url}: {exc}") from exc
    return parse_snapshot(appinfo, url)


def read_appmanifest(path: Path) -> tuple[str, dict[str, str]] | None:
    """Installed build id + per-depot manifest ids from Steam's appmanifest ACF."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    buildid: str | None = None
    manifests: dict[str, str] = {}
    current: str | None = None
    for line in text.splitlines():
        depot = _DEPOT_RE.match(line)
        if depot:
            current = depot.group(1)
            continue
        kv = _KV_RE.match(line)
        if not kv:
            continue
        key, value = kv.group(1), kv.group(2)
        if key == "buildid":
            buildid = value
        elif key == "manifest" and current:
            manifests[current] = value
    if not buildid:
        return None
    return buildid, manifests


def load_pins(path: Path) -> dict[str, Any] | None:
    try:
        with path.open(encoding="utf-8") as fh:
            pins: Any = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        raise SourceError(f"unreadable pins {path}: {exc}") from exc
    if not isinstance(pins, dict) or not isinstance(pins.get("studied"), dict):
        raise SourceError(f"{path}: missing studied block (run --record)")
    return pins


def write_pins(path: Path, pins: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp{os.getpid()}")
    tmp.write_text(json.dumps(pins, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def stock_facts() -> dict[str, Any]:
    """The committed studied-build facts, or {} when absent/unreadable."""
    try:
        with STOCK_FACTS.open(encoding="utf-8") as fh:
            facts: Any = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return {}
    return facts if isinstance(facts, dict) else {}


def record_history(pins: dict[str, Any] | None, studied: dict[str, Any]) -> list[dict[str, Any]]:
    """Previous studied pins, newest first, deduped by build id and capped.

    Steam's content log pairs build ids to manifests, but the log rotates;
    keeping the superseded pins here means an old cached manifest can still be
    labelled with the build that shipped it.
    """
    history: list[dict[str, Any]] = [
        entry for entry in ((pins or {}).get("history") or []) if isinstance(entry, dict)
    ]
    previous = (pins or {}).get("studied")
    if (
        isinstance(previous, dict)
        and previous.get("buildid")
        and previous.get("buildid") != studied.get("buildid")
    ):
        history.insert(
            0,
            {
                "buildid": previous.get("buildid"),
                "gid": previous.get("manifest"),
                "version": previous.get("version"),
                "recorded_utc": previous.get("recorded_utc"),
                "note": "previous studied pin",
            },
        )
    kept: list[dict[str, Any]] = []
    seen: set[str] = set()
    for entry in history:
        key = str(entry.get("buildid") or "")
        if key and key not in seen:
            seen.add(key)
            kept.append(entry)
    return kept[:10]


def select(snapshot: Snapshot, name: str) -> Branch | None:
    for branch in snapshot.branches:
        if branch.name == name:
            return branch
    return None


def fetch_by_name(branch_name: str, label: str, do_fetch: bool) -> int:
    """Hand a branch steamcmd can install even when PICS does not list it."""
    if not LABEL_RE.match(label):
        print(f"steam_builds: invalid label {label!r}", file=sys.stderr)
        return 2
    command = [str(FETCH), branch_name, label]
    if not do_fetch:
        print(" ".join(command))
        return 0
    print("fetch: " + " ".join(command))
    return subprocess.run(command, check=False).returncode


def human_size(value: int | None) -> str:
    return f"{value / 1_000_000_000:.2f} GB" if value else "-"


def iso(epoch: int | None) -> str:
    if not epoch:
        return "-"
    return datetime.fromtimestamp(epoch, tz=timezone.utc).strftime("%Y-%m-%d %H:%MZ")


def as_json(branch: Branch) -> dict[str, Any]:
    return {
        "branch": branch.name,
        "buildid": branch.buildid,
        "manifest": branch.manifest,
        "download_bytes": branch.download,
        "size_bytes": branch.size,
        "updated": branch.updated,
        "description": branch.description,
    }


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="steam_builds.py",
        description="Latest 7DTD dedicated-server build (PICS) + studied-build pin.",
    )
    ap.add_argument("--from", dest="from_path", metavar="FILE", help="read PICS JSON from a file")
    ap.add_argument("--branch", default=None, help="branch to select (default: the pinned one)")
    ap.add_argument("--label", default=None, help="fetch_version.sh label (default: branch name)")
    ap.add_argument("--pins", default=str(PINS), help=f"studied-build pin file (default: {PINS})")
    ap.add_argument(
        "--appmanifest",
        default=str(DEFAULT_APPMANIFEST),
        help="Steam appmanifest ACF of the local install",
    )
    ap.add_argument("--no-installed", action="store_true", help="skip the local install")
    ap.add_argument(
        "--steam-root",
        default=None,
        help="Steam root to scan for cached depot manifests (default: standard locations)",
    )
    ap.add_argument("--json", action="store_true", help="emit the snapshot as JSON")
    ap.add_argument(
        "--check",
        action="store_true",
        help="exit 1 when the selected branch differs from the pin or the install",
    )
    ap.add_argument("--print-fetch", action="store_true", help="print the fetch_version.sh command")
    ap.add_argument("--fetch", action="store_true", help="run fetch_version.sh for the selection")
    ap.add_argument("--record", action="store_true", help="record the selection as the studied pin")
    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    pins_path = Path(args.pins)
    try:
        snapshot = load_appinfo(Path(args.from_path)) if args.from_path else fetch_appinfo(args.url)
        pins = load_pins(pins_path) if pins_path.exists() else None
    except SourceError as exc:
        print(f"steam_builds: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"steam_builds: {exc}", file=sys.stderr)
        return 2

    studied: dict[str, Any] = (pins or {}).get("studied") or {}
    wanted = args.branch or str(studied.get("branch") or "public")
    branch = select(snapshot, wanted)
    if branch is None:
        # A password-gated or brand-new branch (latest_experimental) can be
        # missing from the branch table while steamcmd can still install it by
        # name, so --print-fetch/--fetch fall back to the branch form instead of
        # refusing. There is no build id or manifest to compare in that case.
        if args.print_fetch or args.fetch:
            return fetch_by_name(wanted, args.label or wanted, args.fetch)
        known = ", ".join(b.name for b in snapshot.branches)
        print(
            f"steam_builds: branch {wanted!r} not in {snapshot.source}; known: {known}",
            file=sys.stderr,
        )
        print(
            "steam_builds: pass --print-fetch/--fetch to install it by branch name anyway",
            file=sys.stderr,
        )
        return 2

    installed: tuple[str, dict[str, str]] | None = None
    if not args.no_installed:
        installed = read_appmanifest(Path(args.appmanifest))
    install_buildid = installed[0] if installed else None
    install_manifest = installed[1].get(DEPOT) if installed else None

    roots = roots_from(args.steam_root)
    cached = cached_manifests(DEPOT, roots)
    cached_buildids = steam_log_buildids(DEPOT, roots)
    diffable = sum(1 for b in snapshot.branches if b.manifest in cached)

    if args.json:
        payload = {
            "source": snapshot.source,
            "app": APP,
            "depot": DEPOT,
            "studied": studied or None,
            "installed": (
                {
                    "buildid": install_buildid,
                    "manifest": install_manifest,
                }
                if installed
                else None
            ),
            "selected": as_json(branch),
            "cached_manifests": {
                gid: {"buildid": cached_buildids.get(gid), "path": str(path)}
                for gid, path in sorted(cached.items())
            },
            "branches": [as_json(b) | {"cached": b.manifest in cached} for b in snapshot.branches],
        }
        print(json.dumps(payload, indent=2))
        return 0

    quiet = args.print_fetch and not args.fetch
    if not quiet:
        print(f"source:    {snapshot.source}")
        print(f"app/depot: {APP}/{DEPOT}")
        if installed:
            print(f"installed: buildid {install_buildid} manifest {install_manifest or '-'}")
        else:
            print("installed: not found (set --appmanifest)")
    if not quiet and not args.check:
        print()
        print(f"{'branch':<22} {'buildid':<11} {'manifest':<21} {'size':>10}  {'updated':<17} note")
        for b in snapshot.branches:
            notes = []
            if b.buildid and b.buildid == studied.get("buildid"):
                notes.append("studied")
            if b.buildid and install_buildid and b.buildid == install_buildid:
                notes.append("installed")
            if b.manifest and b.manifest in cached:
                notes.append("cached")
            print(
                f"{b.name:<22} {b.buildid or '-':<11} {b.manifest or '-':<21} "
                f"{human_size(b.size):>10}  {iso(b.updated):<17} {' '.join(notes)}"
            )
        print()
    if not quiet and cached:
        print(
            f"offline-diffable: {diffable} of {len(snapshot.branches)} branch manifests cached "
            f"({len(cached)} manifest(s); steam_manifest.py --history)"
        )
    if not quiet:
        if studied:
            print(
                f"studied pin: branch {studied.get('branch')} buildid {studied.get('buildid')} "
                f"manifest {studied.get('manifest')} "
                f"({studied.get('version') or 'version unknown'})"
            )
        else:
            print(f"studied pin: none in {pins_path}")
        history = [e for e in ((pins or {}).get("history") or []) if isinstance(e, dict)]
        if history:
            earlier = ", ".join(
                f"{e.get('buildid')} ({e.get('gid') or 'gid unknown'})" for e in history[:3]
            )
            print(f"earlier builds: {earlier}" + (" ..." if len(history) > 3 else ""))

    stale = bool(studied) and branch.buildid != studied.get("buildid")
    install_stale = install_buildid is not None and install_buildid != branch.buildid

    if args.record:
        facts = stock_facts()
        studied_entry: dict[str, Any] = {
            "branch": branch.name,
            "buildid": branch.buildid,
            "manifest": branch.manifest,
            "download_bytes": branch.download,
            "size_bytes": branch.size,
            "version": str(facts.get("version", {}).get("display")) or None,
            "dll_sha256": str(facts.get("source_identity", {}).get("assembly_csharp_dll_sha256"))
            or None,
            "recorded_utc": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "source": snapshot.source,
        }
        recorded: dict[str, Any] = {
            "schema": 1,
            "app": APP,
            "depot": DEPOT,
            "studied": studied_entry,
        }
        history = record_history(pins, studied_entry)
        if history:
            recorded["history"] = history
        write_pins(pins_path, recorded)
        print(
            f"recorded: {pins_path} <- {branch.name} buildid {branch.buildid}"
            + (f" (history: {len(history)} earlier build(s))" if history else "")
        )

    label = args.label or branch.name
    if not LABEL_RE.match(label):
        print(f"steam_builds: invalid label {label!r}", file=sys.stderr)
        return 2
    if args.print_fetch or args.fetch:
        if not branch.manifest:
            print(f"steam_builds: branch {branch.name} has no depot {DEPOT} manifest")
            return 2
        command = [str(FETCH), branch.manifest, label]
        if args.print_fetch and not args.fetch:
            print(" ".join(command))
            return 0
        print("fetch: " + " ".join(command))
        return subprocess.run(command, check=False).returncode

    if args.check:
        if not studied:
            print(
                f"steam_builds: FAIL no studied pin in {pins_path} (run --record)", file=sys.stderr
            )
            return 2
        if stale:
            print(
                f"steam_builds: FAIL {branch.name} buildid {branch.buildid} != studied "
                f"{studied.get('buildid')} (newer binary available)",
                file=sys.stderr,
            )
            return 1
        if install_stale:
            print(
                f"steam_builds: FAIL local install buildid {install_buildid} != "
                f"{branch.name} {branch.buildid}",
                file=sys.stderr,
            )
            return 1
        print(f"steam_builds: OK {branch.name} buildid {branch.buildid} matches the studied pin")
        return 0

    if stale or install_stale:
        print("status:    drift (see notes; --check fails, --fetch downloads)")
    else:
        print("status:    up to date")
    return 0


if __name__ == "__main__":
    sys.exit(main())
