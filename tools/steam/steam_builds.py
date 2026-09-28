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
`SOURCE_DATE_EPOCH` (integer UTC epoch) pins that file's `recorded_utc` field,
so re-recording the same build rewrites the same bytes.

Exit codes: 0 ok, 1 drift detected by --check, 2 unusable input/source.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STEAM = Path(__file__).resolve().parent
sys.path.insert(0, str(STEAM))
sys.path.insert(0, str(STEAM.parent))
import tooling  # noqa: E402
from steam_manifest import (  # noqa: E402
    ManifestError,
    VerifyResult,
    cached_manifests,
    read_manifest,
    roots_from,
    steam_log_buildids,
    verify,
)

TOOLS = tooling.TOOLS

PINS = TOOLS / "data" / "steam_builds.json"
STOCK_FACTS = TOOLS / "data" / "stock_facts.json"
FETCH = STEAM / "fetch_version.sh"

APP = "294420"
DEPOT = "294422"  # dedicated-server content depot (linux/windows payload)
PICS_URL = f"https://api.steamcmd.net/v1/info/{APP}"
DEFAULT_APPMANIFEST = next(
    (
        root / "steamapps" / f"appmanifest_{APP}.acf"
        for root in tooling.steam_roots(os.environ, Path.home())
        if (root / "steamapps" / f"appmanifest_{APP}.acf").is_file()
    ),
    # Nothing installed: name the Linux default so the error points somewhere.
    Path.home() / ".local/share/Steam/steamapps" / f"appmanifest_{APP}.acf",
)
# fullmatch, not match with `$`: Python's `$` also matches before a trailing
# newline, so "ok\n" would pass here and only be caught by the shell.
LABEL_RE = re.compile(r"[A-Za-z0-9._-]+")
# A depot manifest gid is numeric. The value reaches steam_builds from the
# PICS response and is handed to fetch_version.sh as an argument, so anything
# non-numeric (in particular a leading `-`, which steamcmd would read as an
# option) is refused rather than forwarded.
GID_RE = re.compile(r"[0-9]+")
FETCH_TIMEOUT_ENV = "RE_STEAM_FETCH_TIMEOUT"
DEFAULT_FETCH_TIMEOUT = 6 * 3600.0


def usable_label(value: str) -> bool:
    """A label fetch_version.sh will accept: fetch_version.sh is the enforcing
    copy (same shape, no bare dot); this keeps the two in step so the refusal
    happens before a download is announced."""
    return bool(LABEL_RE.fullmatch(value)) and value not in (".", "..")


def usable_branch(value: str) -> bool:
    """A branch fetch_version.sh will accept.

    The label shape, plus the one rule the label does not carry: a branch is
    forwarded to `steamcmd -beta <name>`, where a leading `-` is one of
    steamcmd's own options, so it is refused here too.
    """
    return usable_label(value) and not value.startswith("-")


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


@dataclass(frozen=True)
class Integrity:
    """The manifest an install was checked against, and the per-file verdict."""

    manifest: str
    files: VerifyResult


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
    except (AttributeError, KeyError, TypeError) as exc:
        # AttributeError: `depots[depot]` is present but not a mapping, which
        # the same handler turns into the documented SourceError -> exit 2
        # instead of a traceback out of a payload the tool typed as Any.
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
        appinfo: Any = tooling.load_json(path)
    except (OSError, json.JSONDecodeError, tooling.NonFiniteNumberError) as exc:
        raise SourceError(f"unreadable app info {path}: {exc}") from exc
    return parse_snapshot(appinfo, f"file:{path}")


def fetch_appinfo(url: str = PICS_URL, timeout: float = 30.0) -> Snapshot:
    request = urllib.request.Request(url, headers={"User-Agent": "7dtd-engine-research"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            appinfo: Any = tooling.loads_json(response.read().decode("utf-8"))
    except (
        urllib.error.URLError,
        TimeoutError,
        OSError,
        json.JSONDecodeError,
        tooling.NonFiniteNumberError,
    ) as exc:
        raise SourceError(f"cannot read {url}: {exc}") from exc
    return parse_snapshot(appinfo, url)


def read_appmanifest(path: Path) -> tuple[str, dict[str, str]] | None:
    """Installed build id + per-depot manifest ids from Steam's appmanifest ACF."""
    text = _read_text(path)
    if not text:
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


def install_dir_for(appmanifest: Path, override: str | None = None) -> Path | None:
    """The install directory this appmanifest describes (Steam common/<installdir>)."""
    if override:
        return Path(override)
    for line in _read_text(appmanifest).splitlines():
        match = _KV_RE.match(line)
        if match and match.group(1) == "installdir":
            # The ACF is a file, not a trusted authority: an installdir of
            # "../../etc" would point --verify-install at another tree.
            name = match.group(2)
            if not name or "/" in name or "\\" in name or name in (".", ".."):
                return None
            return appmanifest.parent / "common" / name
    return None


def _read_text(path: Path) -> str:
    """Read a Steam config file; absent reads as empty, unreadable as an error.

    A missing appmanifest ACF just means this is not an install Steam tracks, and
    every caller reports that as "not found". A file that exists and cannot be
    read (permissions, an I/O error) is a different failure: returning "" for it
    would report an unreadable config as an absent one and send the operator
    looking for a Steam install that is right there.
    """
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return ""
    except OSError as exc:
        raise SourceError(f"unreadable {path}: {exc}") from exc


def load_pins(path: Path) -> dict[str, Any] | None:
    try:
        pins: Any = tooling.load_json(path)
    except (OSError, json.JSONDecodeError, tooling.NonFiniteNumberError) as exc:
        raise SourceError(f"unreadable pins {path}: {exc}") from exc
    if not isinstance(pins, dict) or not isinstance(pins.get("studied"), dict):
        raise SourceError(f"{path}: missing studied block (run --record)")
    return pins


def write_pins(path: Path, pins: dict[str, Any]) -> None:
    """Replace the pin file atomically, leaving no temp file behind on failure.

    The temp name is pid-scoped so two runs cannot collide, and it is removed
    when the write or the rename fails: a half-written `.json.tmp<pid>` left in
    tools/data/ is the residue of a failed --record, and the next run would
    not clean it up.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp{os.getpid()}")
    try:
        tmp.write_text(json.dumps(pins, indent=2, sort_keys=False) + "\n", encoding="utf-8")
        tmp.replace(path)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise


def stock_facts() -> dict[str, Any]:
    """The committed studied-build facts.

    A missing or corrupt tools/data/stock_facts.json raises: the only caller
    builds the studied entry of the pin file, and the two facts it takes from
    here (the version string and the Assembly-CSharp.dll sha256) are what
    identify that pin later. Reading them as {} would record a committed pin
    with version and dll_sha256 null, which no build-id lookup can ever match.
    """
    try:
        facts: Any = tooling.load_json(STOCK_FACTS)
    except (OSError, json.JSONDecodeError, tooling.NonFiniteNumberError) as exc:
        raise SourceError(
            f"unreadable stock facts {STOCK_FACTS}: {exc} (regenerate with: make stock-sync)"
        ) from exc
    if not isinstance(facts, dict):
        raise SourceError(f"{STOCK_FACTS}: not a JSON object")
    return facts


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
                "dll_sha256": previous.get("dll_sha256"),
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


def fetch_timeout() -> float:
    """Wall-clock bound for a fetch, in seconds.

    A full depot is gigabytes, so this is deliberately far above the mono
    bound; it exists because steamcmd can wait forever on a login prompt or a
    stalled CDN, and nothing else in this tool can end that. `RE_STEAM_FETCH_TIMEOUT`
    raises it for a slow line; a non-numeric or non-positive value fails loud
    rather than meaning "no bound", by the shared rule in `tooling`.
    """
    return tooling.positive_seconds(FETCH_TIMEOUT_ENV, DEFAULT_FETCH_TIMEOUT)


def run_fetch(command: list[str]) -> int:
    """Run fetch_version.sh under that bound, killing steamcmd's group with it.

    fetch_version.sh spawns steamcmd and then a `find` over the depot tree, so
    the process group is what has to die: killing only the script would leave
    a download running with no parent.
    """
    try:
        timeout = fetch_timeout()
    except tooling.ConfigError as exc:
        # An unusable RE_STEAM_FETCH_TIMEOUT is this tool's "unusable input"
        # exit 2, not a traceback: the module header promises that code.
        print(f"steam_builds: {exc}", file=sys.stderr)
        return 2
    rc, _, err = tooling.run_bounded(command, env=dict(os.environ), timeout=timeout)
    if rc != 0 and err.strip():
        print(err.strip(), file=sys.stderr)
    return rc


def fetch_argv(branch: Branch, source: str, label: str) -> tuple[list[str] | None, int]:
    """The `fetch_version.sh` argv for a branch, or `(None, rc)` when refused.

    Both output paths need the same two refusals, and a branch that changes
    between them must not be fetched under one rule and refused under the
    other: a branch with no depot manifest, and a manifest gid that is not
    numeric (it reaches steamcmd as an argument, where a leading `-` reads as
    an option).
    """
    if not branch.manifest:
        print(f"steam_builds: branch {branch.name} has no depot {DEPOT} manifest")
        return None, 2
    if not GID_RE.fullmatch(branch.manifest):
        print(
            f"steam_builds: refusing to fetch with a non-numeric depot manifest "
            f"gid {branch.manifest!r} from {source}",
            file=sys.stderr,
        )
        return None, 2
    return [str(FETCH), branch.manifest, label], 0


def fetch_by_name(branch_name: str, label: str, do_fetch: bool) -> int:
    """Hand a branch steamcmd can install even when PICS does not list it."""
    if not usable_label(label):
        print(f"steam_builds: invalid label {label!r}", file=sys.stderr)
        return 2
    if not usable_branch(branch_name):
        print(f"steam_builds: invalid branch name {branch_name!r}", file=sys.stderr)
        return 2
    command = [str(FETCH), branch_name, label]
    if not do_fetch:
        print(" ".join(command))
        return 0
    print("fetch: " + " ".join(command))
    return run_fetch(command)


def human_size(value: int | None) -> str:
    return f"{value / 1_000_000_000:.2f} GB" if value else "-"


def iso(epoch: int | None) -> str:
    if not epoch:
        return "-"
    try:
        stamp = datetime.fromtimestamp(epoch, tz=timezone.utc)
    except (OverflowError, OSError, ValueError):
        return "-"
    return stamp.strftime("%Y-%m-%d %H:%MZ")


def drift_verdict(
    branch: Branch,
    studied: dict[str, Any] | None,
    install_buildid: str | None,
    integrity: Integrity | None,
    pins_path: Path,
) -> tuple[int, str] | None:
    """The --check verdict as (exit code, FAIL reason), or None when clean.

    Shared by the human table and the --json snapshot, so `--check --json`
    cannot report success on a drifted build.
    """
    if integrity and (integrity.files.missing or integrity.files.bad):
        return 1, (
            f"local install differs from Steam's manifest "
            f"({integrity.files.bad} mismatch, {integrity.files.missing} missing)"
        )
    if not studied:
        return 2, f"no studied pin in {pins_path} (run --record)"
    if branch.buildid != studied.get("buildid"):
        return 1, (
            f"{branch.name} buildid {branch.buildid} != studied "
            f"{studied.get('buildid')} (newer binary available)"
        )
    if install_buildid is not None and install_buildid != branch.buildid:
        return 1, f"local install buildid {install_buildid} != {branch.name} {branch.buildid}"
    return None


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
    ap.add_argument(
        "--pins",
        default=None,
        metavar="FILE",
        help=f"studied-build pin file (default: {PINS}, which may be absent until --record)",
    )
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
    ap.add_argument(
        "--install-dir",
        default=None,
        help="install directory to verify (default: the appmanifest's Steam common/<installdir>)",
    )
    ap.add_argument(
        "--ignore",
        action="append",
        default=[],
        metavar="SUBSTR",
        help="skip manifest paths containing SUBSTR when verifying (repeatable; "
        "for files the server rewrites at runtime, e.g. platform.cfg)",
    )
    ap.add_argument(
        "--verify-install",
        nargs="?",
        const="",
        default=None,
        metavar="SUBSTR",
        help="hash local files against Steam's manifest for the installed build "
        "(optionally limited to paths containing SUBSTR; without a filter this reads the whole install)",
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
    # The default pin file, and any --pins file this run will write, is allowed
    # to be absent (--record creates it). A named file nothing writes is not: a
    # typo there reads as "studied pin: none" and exits 0, quietly dropping the
    # drift comparison the run exists for.
    pins_path = Path(args.pins) if args.pins else PINS
    if args.pins and not args.record and not pins_path.exists():
        print(f"steam_builds: --pins file not found: {pins_path}", file=sys.stderr)
        return 2
    try:
        snapshot = load_appinfo(Path(args.from_path)) if args.from_path else fetch_appinfo()
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
        try:
            installed = read_appmanifest(Path(args.appmanifest))
        except SourceError as exc:
            print(f"steam_builds: {exc}", file=sys.stderr)
            return 2
    install_buildid = installed[0] if installed else None
    install_manifest = installed[1].get(DEPOT) if installed else None

    roots = roots_from(args.steam_root)
    cached = cached_manifests(DEPOT, roots)
    cached_buildids = steam_log_buildids(DEPOT, roots)
    diffable = sum(1 for b in snapshot.branches if b.manifest in cached)

    integrity: Integrity | None = None
    if args.verify_install is not None:
        gid = install_manifest or branch.manifest
        manifest_path = cached.get(gid or "")
        if manifest_path is None:
            print(
                f"steam_builds: no cached manifest for the installed build "
                f"({gid or 'unknown gid'}); fetch it or point --steam-root at the right tree",
                file=sys.stderr,
            )
            return 2
        try:
            root = install_dir_for(Path(args.appmanifest), args.install_dir)
        except SourceError as exc:
            print(f"steam_builds: {exc}", file=sys.stderr)
            return 2
        if root is None or not root.is_dir():
            print(
                f"steam_builds: cannot locate the install directory "
                f"({root or args.appmanifest}); pass --install-dir",
                file=sys.stderr,
            )
            return 2
        try:
            files = verify(
                read_manifest(manifest_path),
                root,
                args.verify_install or None,
                tuple(args.ignore),
            )
        except ManifestError as exc:
            print(f"steam_builds: {exc}", file=sys.stderr)
            return 2
        integrity = Integrity(manifest_path.name, files)

    label = args.label or branch.name
    if not usable_label(label):
        print(f"steam_builds: invalid label {label!r}", file=sys.stderr)
        return 2

    if args.record:
        try:
            facts = stock_facts()
        except SourceError as exc:
            print(f"steam_builds: {exc}", file=sys.stderr)
            return 2
        try:
            recorded_utc = tooling.generation_stamp()
        except tooling.StampError as exc:
            print(f"steam_builds: {exc}", file=sys.stderr)
            return 2
        studied_entry: dict[str, Any] = {
            "branch": branch.name,
            "buildid": branch.buildid,
            "manifest": branch.manifest,
            "download_bytes": branch.download,
            "size_bytes": branch.size,
            "version": facts.get("version", {}).get("display") or None,
            "dll_sha256": facts.get("source_identity", {}).get("assembly_csharp_dll_sha256")
            or None,
            "recorded_utc": recorded_utc,
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
        # The pin now IS the recorded entry: every later verdict, the printed
        # pin line and the JSON payload must read the pin the file carries,
        # not the one this process loaded before --record rewrote it.
        pins = recorded
        studied = studied_entry
        # --json owns stdout, so the human confirmation goes beside the JSON.
        print(
            f"recorded: {pins_path} <- {branch.name} buildid {branch.buildid}"
            + (f" (history: {len(history)} earlier build(s))" if history else ""),
            file=sys.stderr if args.json else sys.stdout,
        )

    if args.json:
        # --fetch/--print-fetch act on the selection, and --json only changes
        # how the snapshot is printed. Silently dropping the fetch here made
        # both options no-ops in a scripted run.
        fetch_command: list[str] | None = None
        if args.print_fetch or args.fetch:
            fetch_command, rc = fetch_argv(branch, snapshot.source, label)
            if fetch_command is None:
                return rc
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
            "integrity": (
                {
                    "manifest": integrity.manifest,
                    "ok": integrity.files.ok,
                    "missing": integrity.files.missing,
                    "mismatch": integrity.files.bad,
                    "ignored": integrity.files.ignored,
                    "problems": integrity.files.problems[:50],
                }
                if integrity
                else None
            ),
            "cached_manifests": {
                gid: {"buildid": cached_buildids.get(gid), "path": str(path)}
                for gid, path in sorted(cached.items())
            },
            "branches": [as_json(b) | {"cached": b.manifest in cached} for b in snapshot.branches],
        }
        print(json.dumps(payload, indent=2))
        fetch_rc = 0
        if fetch_command is not None:
            if args.print_fetch and not args.fetch:
                # stdout is the JSON document, so the command goes to stderr.
                print(" ".join(fetch_command), file=sys.stderr)
            else:
                print("fetch: " + " ".join(fetch_command), file=sys.stderr)
                fetch_rc = run_fetch(fetch_command)
        if args.check:
            verdict = drift_verdict(branch, studied, install_buildid, integrity, pins_path)
            if verdict is not None:
                code, message = verdict
                print(f"steam_builds: FAIL {message}", file=sys.stderr)
                return code
        return fetch_rc

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
    if integrity:
        files = integrity.files
        for line in files.problems[:20]:
            print(line, file=sys.stderr)
        if len(files.problems) > 20:
            print(f"... ({len(files.problems) - 20} more)", file=sys.stderr)
        print(
            f"integrity: {files.ok} ok, {files.missing} missing, {files.bad} mismatch"
            + (f", {files.ignored} ignored" if files.ignored else "")
            + f" against {integrity.manifest}"
        )
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

    if args.print_fetch or args.fetch:
        command, rc = fetch_argv(branch, snapshot.source, label)
        if command is None:
            return rc
        if args.print_fetch and not args.fetch:
            print(" ".join(command))
            return 0
        print("fetch: " + " ".join(command))
        return run_fetch(command)

    if args.check:
        verdict = drift_verdict(branch, studied, install_buildid, integrity, pins_path)
        if verdict is not None:
            code, message = verdict
            print(f"steam_builds: FAIL {message}", file=sys.stderr)
            return code
        print(f"steam_builds: OK {branch.name} buildid {branch.buildid} matches the studied pin")
        return 0

    if stale or install_stale:
        print("status:    drift (see notes; --check fails, --fetch downloads)")
    else:
        print("status:    up to date")
    return 0


if __name__ == "__main__":
    sys.exit(main())
