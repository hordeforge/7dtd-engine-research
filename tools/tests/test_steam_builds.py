#!/usr/bin/env python3
"""steam_builds.py: PICS parse, drift verdicts, and the committed studied pin.

Network-free and DLL-free: every case feeds the tool a fixture app-info payload
via --from, a fixture appmanifest via --appmanifest, and a temp pin file. Also
checks that the committed tools/data/steam_builds.json names the build whose
bytes are pinned in tools/data/stock_facts.json, so a diff narrative cannot cite
a Steam build the corpus did not hash.

Usage: python3 tools/tests/test_steam_builds.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

sys.path.insert(0, str(_common.TOOLS / "steam"))
import steam_builds

SCRIPT = _common.TOOLS / "steam" / "steam_builds.py"
PINS = _common.TOOLS / "data" / "steam_builds.json"
STOCK_FACTS = _common.TOOLS / "data" / "stock_facts.json"

APPINFO = {
    "status": "success",
    "data": {
        "294420": {
            "depots": {
                "branches": {
                    "public": {"buildid": "100", "timebuildupdated": "1700000000"},
                    "v9.9.9": {"buildid": "90", "timebuildupdated": "1600000000"},
                    "alpha9.3": {"buildid": "5", "timebuildupdated": "1400000000"},
                    "rogue": {"buildid": "7", "timebuildupdated": "1500000000"},
                },
                "294422": {
                    "manifests": {
                        "public": {"gid": "111", "size": "1000", "download": "500"},
                        "v9.9.9": {"gid": "222", "size": "900", "download": "400"},
                        "rogue": {"gid": "-injected", "size": "900", "download": "400"},
                    }
                },
            }
        }
    },
}

ACF = """"AppState"
{
\t"appid"\t\t"294420"
\t"installdir"\t\t"fake"
\t"buildid"\t\t"__BUILDID__"
\t"InstalledDepots"
\t{
\t\t"294422"
\t\t{
\t\t\t"manifest"\t\t"111"
\t\t}
\t}
}
"""


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )


def check_error_paths(tmp_path: Path, appinfo: Path) -> None:
    """A read that fails must not read as a read that found nothing.

    An appmanifest ACF that exists but cannot be read is an operator error, not
    an install Steam does not track: the tool says so and exits 2 rather than
    printing "installed: not found". --record must refuse to write a pin whose
    version and dll_sha256 it could not read, and a failed pin write must leave
    no temp file behind.
    """
    unreadable_acf = tmp_path / "appmanifest.d"
    unreadable_acf.mkdir()
    denied = run("--from", str(appinfo), "--appmanifest", str(unreadable_acf), "--no-installed")
    assert denied.returncode == 0, denied  # --no-installed never reads the ACF

    denied = run("--from", str(appinfo), "--appmanifest", str(unreadable_acf))
    assert denied.returncode == 2, denied
    assert "unreadable" in denied.stderr, denied.stderr
    assert str(unreadable_acf) in denied.stderr, denied.stderr

    missing_acf = run("--from", str(appinfo), "--appmanifest", str(tmp_path / "nope.acf"))
    assert missing_acf.returncode == 0, missing_acf
    assert "installed: not found" in missing_acf.stdout, missing_acf.stdout

    corrupt = tmp_path / "stock_facts.json"
    corrupt.write_text('{"not json', encoding="utf-8")
    saved = steam_builds.STOCK_FACTS
    try:
        for bad in (corrupt, tmp_path / "absent.json"):
            steam_builds.STOCK_FACTS = bad
            try:
                steam_builds.stock_facts()
            except steam_builds.SourceError as exc:
                message = str(exc)
            else:
                raise AssertionError(f"stock_facts() accepted an unreadable {bad}")
            assert str(bad) in message, message
            assert "stock-sync" in message, message

        not_object = tmp_path / "facts_list.json"
        not_object.write_text("[1, 2]", encoding="utf-8")
        steam_builds.STOCK_FACTS = not_object
        try:
            steam_builds.stock_facts()
        except steam_builds.SourceError as exc:
            message = str(exc)
        else:
            raise AssertionError("stock_facts() accepted a non-object payload")
        assert "not a JSON object" in message, message
    finally:
        steam_builds.STOCK_FACTS = saved

    # A pin write that fails at the rename must not leave its temp file: the
    # target here is a directory, so replace() fails after the temp file exists.
    pinned_dir = tmp_path / "pins_as_dir"
    pinned_dir.mkdir()
    try:
        steam_builds.write_pins(pinned_dir, {"studied": {}})
    except OSError:
        pass
    else:
        raise AssertionError("write_pins() replaced a directory with a file")
    residue = [p.name for p in tmp_path.iterdir() if p.name.startswith(".pins_as_dir.tmp")]
    assert not residue, f"write_pins left temp files behind: {residue}"

    steam_builds.write_pins(tmp_path / "clean.json", {"studied": {"buildid": "1"}})
    assert (
        json.loads((tmp_path / "clean.json").read_text(encoding="utf-8"))["studied"]["buildid"]
        == "1"
    )
    assert not [p for p in tmp_path.iterdir() if p.name.startswith(".clean.json.tmp")], (
        "write_pins left a temp file behind on the success path"
    )


def check_committed_pin() -> None:
    pins = json.loads(PINS.read_text(encoding="utf-8"))
    studied = pins["studied"]
    assert pins["app"] == "294420", pins
    assert pins["depot"] == "294422", pins
    for key in ("branch", "buildid", "manifest"):
        assert studied.get(key), f"studied.{key} missing: {studied}"
    facts = json.loads(STOCK_FACTS.read_text(encoding="utf-8"))
    assert studied["version"] == facts["version"]["display"], (
        f"pin version {studied['version']!r} != stock_facts {facts['version']['display']!r}"
    )
    assert studied["dll_sha256"] == facts["source_identity"]["assembly_csharp_dll_sha256"], (
        "pin dll_sha256 must be the hashed studied build"
    )


def main() -> None:
    help_run = run("--help")
    assert help_run.returncode == 0, help_run
    assert "usage:" in help_run.stdout.lower(), help_run

    with tempfile.TemporaryDirectory(prefix="steam_builds_", dir=_common.scratch_dir()) as tmp:
        tmp_path = Path(tmp)
        appinfo = tmp_path / "appinfo.json"
        appinfo.write_text(json.dumps(APPINFO), encoding="utf-8")
        bad = tmp_path / "bad.json"
        bad.write_text(json.dumps({"data": {"294420": {}}}), encoding="utf-8")
        good_pins = tmp_path / "pins.json"
        good_pins.write_text(
            json.dumps({"schema": 1, "studied": {"branch": "public", "buildid": "100"}}),
            encoding="utf-8",
        )
        stale_pins = tmp_path / "stale.json"
        stale_pins.write_text(
            json.dumps({"schema": 1, "studied": {"branch": "public", "buildid": "90"}}),
            encoding="utf-8",
        )
        no_pins = tmp_path / "none.json"
        no_pins.write_text(json.dumps({"schema": 1}), encoding="utf-8")
        acf = tmp_path / "appmanifest.acf"
        acf.write_text(ACF.replace("__BUILDID__", "100"), encoding="utf-8")
        stale_acf = tmp_path / "stale.acf"
        stale_acf.write_text(ACF.replace("__BUILDID__", "90"), encoding="utf-8")
        out_pins = tmp_path / "recorded.json"

        # Steam root fixture: one cached manifest (gid 111), no others.
        steam_root = tmp_path / "steam"
        (steam_root / "depotcache").mkdir(parents=True)
        (steam_root / "logs").mkdir()
        encoder = _common.load_sibling("test_steam_manifest")
        stock_bytes = b"stock managed bytes\n"
        install = tmp_path / "common" / "fake"
        (install / "Data" / "Managed").mkdir(parents=True)
        (install / "Data" / "Managed" / "Good.dll").write_bytes(stock_bytes)
        (steam_root / "depotcache" / "294422_111.manifest").write_bytes(
            encoder.manifest([encoder.entry("Data\\Managed\\Good.dll", stock_bytes)])
        )
        (steam_root / "logs" / "content_log.txt").write_text(
            "[2026-01-01 00:00:00] AppID 294420 finished update, 1 mounted depots "
            "(BuildID 100) : 294422 (111),\n",
            encoding="utf-8",
        )
        base = ("--from", str(appinfo), "--appmanifest", str(acf), "--steam-root", str(steam_root))
        table = run(*base, "--pins", str(good_pins))
        assert table.returncode == 0, table.stderr
        assert "installed: buildid 100" in table.stdout, table.stdout
        assert "public" in table.stdout, table.stdout
        assert "111" in table.stdout, table.stdout
        assert "offline-diffable: 1 of 4 branch manifests cached" in table.stdout, table.stdout
        assert "cached" in table.stdout, table.stdout

        js = run(*base, "--pins", str(good_pins), "--json", "--branch", "v9.9.9")
        assert js.returncode == 0, js.stderr
        payload = json.loads(js.stdout)
        assert payload["selected"]["buildid"] == "90", payload["selected"]
        assert payload["selected"]["manifest"] == "222", payload["selected"]
        assert payload["installed"]["buildid"] == "100", payload["installed"]
        assert len(payload["branches"]) == 4, payload["branches"]
        assert payload["cached_manifests"]["111"]["buildid"] == "100", payload["cached_manifests"]
        selected_branch = next(b for b in payload["branches"] if b["branch"] == "public")
        assert selected_branch["cached"] is True, selected_branch

        ok = run(*base, "--pins", str(good_pins), "--check")
        assert ok.returncode == 0, (ok.returncode, ok.stdout, ok.stderr)
        assert "OK" in ok.stdout, ok.stdout

        drifted = run(*base, "--pins", str(stale_pins), "--check")
        assert drifted.returncode == 1, drifted
        assert "FAIL" in drifted.stderr, drifted.stderr

        install_drift = run(
            "--from",
            str(appinfo),
            "--appmanifest",
            str(stale_acf),
            "--pins",
            str(good_pins),
            "--check",
        )
        assert install_drift.returncode == 1, install_drift
        assert "local install" in install_drift.stderr, install_drift.stderr

        unreadable = run(*base, "--pins", str(bad), "--check")
        assert unreadable.returncode == 2, unreadable

        assert run(*base, "--pins", str(no_pins), "--check").returncode == 2

        source_error = run("--from", str(bad), "--no-installed", "--pins", str(good_pins), "--json")
        assert source_error.returncode == 2, source_error
        assert "app info" in source_error.stderr, source_error.stderr

        missing = run("--from", str(appinfo), "--no-installed", "--branch", "latest_experimental")
        assert missing.returncode == 2, missing

        # A branch PICS does not list can still be installed by name.
        unlisted = run(
            "--from",
            str(appinfo),
            "--no-installed",
            "--branch",
            "latest_experimental",
            "--print-fetch",
        )
        assert unlisted.returncode == 0, unlisted.stderr
        unlisted_lines = [line for line in unlisted.stdout.splitlines() if line.strip()]
        assert len(unlisted_lines) == 1, unlisted_lines
        assert unlisted_lines[0].endswith("latest_experimental latest_experimental"), unlisted_lines

        fetch = run(*base, "--pins", str(good_pins), "--print-fetch", "--branch", "v9.9.9")
        assert fetch.returncode == 0, fetch.stderr
        lines = [line for line in fetch.stdout.splitlines() if line.strip()]
        assert len(lines) == 1, lines
        assert lines[0].endswith("222 v9.9.9"), lines

        # A PICS gid reaches fetch_version.sh as a steamcmd argument, so a
        # non-numeric one (a leading `-` reads as an option) is refused.
        rogue_gid = run(*base, "--pins", str(good_pins), "--print-fetch", "--branch", "rogue")
        assert rogue_gid.returncode == 2, (rogue_gid.stdout, rogue_gid.stderr)
        assert "non-numeric depot manifest" in rogue_gid.stderr, rogue_gid.stderr

        # A label becomes a filename and a steamcmd argument, so anything
        # outside [A-Za-z0-9._-] is refused, trailing newline included.
        for bad_label in ("../escape", "a b", "a\n"):
            refused_label = run(
                *base, "--pins", str(good_pins), "--print-fetch", "--label", bad_label
            )
            assert refused_label.returncode == 2, (bad_label, refused_label.stdout)
            assert "invalid label" in refused_label.stderr, (bad_label, refused_label.stderr)

        recorded = run(*base, "--pins", str(out_pins), "--record", "--branch", "v9.9.9")
        assert recorded.returncode == 0, recorded.stderr
        written = json.loads(out_pins.read_text(encoding="utf-8"))["studied"]
        assert written["buildid"] == "90", written
        assert written["manifest"] == "222", written

        # Install integrity against Steam's manifest for the installed build.
        clean = run(*base, "--pins", str(good_pins), "--verify-install", "Data")
        assert clean.returncode == 0, (clean.stdout, clean.stderr)
        assert "integrity: 1 ok, 0 missing, 0 mismatch" in clean.stdout, clean.stdout

        integrity_json = run(*base, "--pins", str(good_pins), "--verify-install", "Data", "--json")
        payload = json.loads(integrity_json.stdout)
        assert payload["integrity"]["ok"] == 1, payload["integrity"]
        assert payload["integrity"]["manifest"] == "294422_111.manifest", payload["integrity"]

        ignored = run(
            *base,
            "--pins",
            str(good_pins),
            "--verify-install",
            "Data",
            "--ignore",
            "Good.dll",
        )
        assert ignored.returncode == 0, (ignored.stdout, ignored.stderr)
        assert "integrity: 0 ok, 0 missing, 0 mismatch, 1 ignored" in ignored.stdout, ignored.stdout

        (install / "Data" / "Managed" / "Good.dll").write_bytes(b"tampered")
        broken = run(*base, "--pins", str(good_pins), "--check", "--verify-install", "Data")
        assert broken.returncode == 1, (broken.stdout, broken.stderr)
        assert "integrity: 0 ok, 0 missing, 1 mismatch" in broken.stdout, broken.stdout
        assert "FAIL local install differs" in broken.stderr, broken.stderr

        empty = tmp_path / "empty-install"
        empty.mkdir()
        gone = run(
            *base,
            "--pins",
            str(good_pins),
            "--check",
            "--verify-install",
            "--install-dir",
            str(empty),
        )
        assert gone.returncode == 1, (gone.stdout, gone.stderr)
        assert "1 missing" in gone.stdout, gone.stdout

        # An ACF is a file, not a trusted authority: an installdir naming a
        # parent tree must not make --verify-install hash outside the install.
        escape_acf = tmp_path / "escape.acf"
        escape_acf.write_text(
            ACF.replace("__BUILDID__", "100").replace(
                '"installdir"\t\t"fake"', '"installdir"\t\t"../../.."'
            ),
            encoding="utf-8",
        )
        escaped = run(
            "--from",
            str(appinfo),
            "--pins",
            str(good_pins),
            "--appmanifest",
            str(escape_acf),
            "--steam-root",
            str(steam_root),
            "--verify-install",
            "Data",
        )
        assert escaped.returncode == 2, (escaped.stdout, escaped.stderr)
        assert "cannot locate the install directory" in escaped.stderr, escaped.stderr

        seeded = tmp_path / "seeded.json"
        seeded.write_text(
            json.dumps(
                {
                    "schema": 1,
                    "studied": {
                        "branch": "public",
                        "buildid": "100",
                        "manifest": "111",
                        "version": "V 0.0.1",
                    },
                }
            ),
            encoding="utf-8",
        )
        first = run(*base, "--pins", str(seeded), "--record", "--branch", "v9.9.9")
        assert first.returncode == 0, first.stderr
        assert "history: 1 earlier build(s)" in first.stdout, first.stdout
        seeded_doc = json.loads(seeded.read_text(encoding="utf-8"))
        assert seeded_doc["studied"]["buildid"] == "90", seeded_doc
        assert [e["buildid"] for e in seeded_doc["history"]] == ["100"], seeded_doc
        assert seeded_doc["history"][0]["gid"] == "111", seeded_doc

        again = run(*base, "--pins", str(seeded), "--record", "--branch", "v9.9.9")
        assert again.returncode == 0, again.stderr
        assert "earlier builds: 100 (111)" in again.stdout, again.stdout
        repeat_doc = json.loads(seeded.read_text(encoding="utf-8"))
        assert [e["buildid"] for e in repeat_doc["history"]] == ["100"], repeat_doc

        check_error_paths(tmp_path, appinfo)

    check_committed_pin()
    print("OK: steam_builds parse/drift/pin cases pass; committed pin matches stock_facts")


if __name__ == "__main__":
    main()
