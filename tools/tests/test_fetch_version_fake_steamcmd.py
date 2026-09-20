#!/usr/bin/env python3
"""End-to-end check of parity/fetch_version.sh with a recording fake steamcmd.

The download path was the one documented entry point with no test: it needs
SteamCMD and a multi-GB depot, so nothing exercised manifest pass-through, the
STEAM_CONTENT lookup, the DLL copy, the ParitySurface compile/run step, the
atomic publish, or the fail-closed branches. A fake steamcmd that records its
argv and copies a known DLL covers all of it offline.

Cases:
  1. manifest form   -> snapshot written, identical to a direct ParitySurface run
  2. two builds      -> gid-mapped fetches reproduce both snapshots; wire parity is unchanged
  3. branch form     -> snapshot written from the install dir
  4. steam_builds --fetch -> branch manifest reaches fetch_version.sh
  5. fake does nothing -> non-zero, no snapshot published
  6. fake fails      -> non-zero, no snapshot published

SKIPs without mono/mcs, the pinned Cecil build, or the live dedicated DLL.

Usage: python3 tools/tests/test_fetch_version_fake_steamcmd.py
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _common

FETCH = _common.TOOLS / "parity" / "fetch_version.sh"
PARITY_EXE = _common.BIN / "ParitySurface.exe"

FAKE = """#!/usr/bin/env bash
# Recording fake steamcmd: logs argv, then materialises a DLL for either form.
set -u
printf '%s\\n' "$*" >> "${FAKE_LOG:?}"
case "${FAKE_MODE:-ok}" in
  fail) exit 7 ;;
  nothing) exit 0 ;;
esac
dir=""
mode=manifest
while [[ $# -gt 0 ]]; do
  case "$1" in
    +download_depot)
      shift
      app="${1:-0}"; shift || true
      depot="${1:-0}"; shift || true
      printf 'manifest=%s\\n' "${1:-}" >> "${FAKE_LOG}"
      shift || true
      dir="${STEAM_CONTENT:?}/app_${app}/depot_${depot}/7DaysToDieServer_Data/Managed"
      ;;
    +force_install_dir)
      shift
      dir="${1:-}/7DaysToDieServer_Data/Managed"
      mode=branch
      shift || true
      ;;
    *) shift || true ;;
  esac
done
[[ -n "$dir" ]] || exit 9
mkdir -p "$dir"
dll="${FAKE_DLL:?}"
if [[ -n "${FAKE_DLL_MAP:-}" ]]; then
  # <gid>=<path> pairs, ';' separated: lets one fake serve several builds.
  saved="$IFS"; IFS=';'
  for pair in $FAKE_DLL_MAP; do
    [[ "${pair%%=*}" == "${manifest:-}" ]] && dll="${pair#*=}"
  done
  IFS="$saved"
fi
cp -f "$dll" "$dir/Assembly-CSharp.dll"
printf 'mode=%s\\n' "$mode" >> "${FAKE_LOG}"
"""


def load_snapshot(text: str) -> dict[str, object]:
    start = text.index("{")
    data: dict[str, object] = json.loads(text[start:])
    return data


def direct_snapshot(dll: Path) -> dict[str, object]:
    env = dict(os.environ, MONO_PATH=str(_common.BIN))
    proc = subprocess.run(
        ["mono", str(PARITY_EXE), str(dll)], capture_output=True, text=True, env=env
    )
    assert proc.returncode == 0, proc.stderr
    return load_snapshot(proc.stdout)


def main() -> None:
    asm = _common.find_asm()
    if asm is None:
        print("SKIP: dedicated Assembly-CSharp.dll not found")
        return
    if shutil.which("mono") is None or shutil.which("mcs") is None:
        print("SKIP: mono/mcs not on PATH")
        return
    if not (_common.BIN / "Mono.Cecil.dll").is_file() or not PARITY_EXE.is_file():
        print("SKIP: parity tools not built (cd tools && ./build.sh --skip-legacy)")
        return

    with tempfile.TemporaryDirectory(prefix="fetch_version_", dir=_common.scratch_dir()) as tmp:
        root = Path(tmp)
        fake = root / "steamcmd.sh"
        fake.write_text(FAKE, encoding="utf-8")
        fake.chmod(0o755)
        log = root / "calls.log"
        content = root / "content"
        base_env = dict(
            os.environ,
            STEAMCMD=str(fake),
            FAKE_DLL=str(asm),
            FAKE_LOG=str(log),
            STEAM_CONTENT=str(content),
        )

        def fetch(
            target: str, label: str, mode: str, out: Path, content: Path
        ) -> subprocess.CompletedProcess[str]:
            # A fresh content root per case: steamcmd reuses its content dir, so a
            # shared one would let an earlier download mask a steamcmd that did
            # nothing.
            env = dict(
                base_env,
                FAKE_MODE=mode,
                STEAM_CONTENT=str(content),
                SCRATCH=str(root / "scratch" / label),
                OUT=str(out),
            )
            return subprocess.run(
                [str(FETCH), target, label], capture_output=True, text=True, env=env
            )

        # 1. manifest form: pass-through, atomic publish, snapshot equality
        out = root / "out-manifest"
        proc = fetch("1633674551820196085", "faketest", "ok", out, root / "content-manifest")
        assert proc.returncode == 0, (proc.stdout, proc.stderr)
        snapshot = out / "parity_faketest.json"
        assert snapshot.is_file(), proc.stdout
        assert "wrote" in proc.stdout, proc.stdout
        assert load_snapshot(snapshot.read_text(encoding="utf-8")) == direct_snapshot(asm)
        calls = log.read_text(encoding="utf-8")
        assert "manifest=1633674551820196085" in calls, calls

        # 2. branch form: install-dir form must materialise the DLL too
        out_branch = root / "out-branch"
        branch = fetch("v3.1.0", "fakebranch", "ok", out_branch, root / "content-branch")
        assert branch.returncode == 0, (branch.stdout, branch.stderr)
        assert (out_branch / "parity_fakebranch.json").is_file(), branch.stdout
        assert "mode=branch" in log.read_text(encoding="utf-8")

        # 2. one fake, two builds: gid-mapped fetches must reproduce both snapshots,
        # and the wire surface must come out unchanged (changelog-3.2.0 section 8).
        backup = asm.with_name(asm.name + ".re_stock_bak")
        if backup.is_file():
            mapped = f"1633674551820196085={asm};1712639873522480804={backup}"
            pairs = [
                ("1633674551820196085", "map-b10", asm),
                ("1712639873522480804", "map-b9", backup),
            ]
            for gid, label, dll in pairs:
                out_map = root / f"out-{label}"
                env_map = dict(
                    base_env,
                    FAKE_MODE="ok",
                    FAKE_DLL_MAP=mapped,
                    STEAM_CONTENT=str(root / f"content-{label}"),
                    SCRATCH=str(root / "scratch" / label),
                    OUT=str(out_map),
                )
                proc_map = subprocess.run(
                    [str(FETCH), gid, label], capture_output=True, text=True, env=env_map
                )
                assert proc_map.returncode == 0, (proc_map.stdout, proc_map.stderr)
                snapshot_map = out_map / f"parity_{label}.json"
                assert snapshot_map.is_file(), proc_map.stdout
                assert load_snapshot(snapshot_map.read_text(encoding="utf-8")) == direct_snapshot(
                    dll
                ), f"{label}: fetched snapshot != direct ParitySurface run"

            wire = subprocess.run(
                [
                    sys.executable,
                    str(_common.TOOLS / "parity" / "parity_diff.py"),
                    str(root / "out-map-b9" / "parity_map-b9.json"),
                    str(root / "out-map-b10" / "parity_map-b10.json"),
                ],
                capture_output=True,
                text=True,
            )
            assert wire.returncode == 0, wire.stdout
            assert "changed wire (0)" in wire.stdout, wire.stdout
        else:
            print(f"note: {backup.name} absent; b9/b10 gid-map case skipped")

        # 3. steam_builds --fetch must hand the branch's manifest to fetch_version.sh
        appinfo = root / "appinfo.json"
        appinfo.write_text(
            json.dumps(
                {
                    "status": "success",
                    "data": {
                        "294420": {
                            "depots": {
                                "branches": {"public": {"buildid": "100"}},
                                "294422": {
                                    "manifests": {
                                        "public": {
                                            "gid": "1633674551820196085",
                                            "size": "1",
                                            "download": "1",
                                        }
                                    }
                                },
                            }
                        }
                    },
                }
            ),
            encoding="utf-8",
        )
        pins = root / "pins.json"
        pins.write_text(
            json.dumps({"schema": 1, "studied": {"branch": "public", "buildid": "100"}}),
            encoding="utf-8",
        )
        builds_log = root / "calls-builds.log"
        out_builds = root / "out-builds"
        builds = subprocess.run(
            [
                sys.executable,
                str(_common.TOOLS / "parity" / "steam_builds.py"),
                "--from",
                str(appinfo),
                "--pins",
                str(pins),
                "--no-installed",
                "--steam-root",
                str(root / "empty-root"),
                "--fetch",
                "--label",
                "fakebuilds",
            ],
            capture_output=True,
            text=True,
            env=dict(
                base_env,
                FAKE_LOG=str(builds_log),
                FAKE_MODE="ok",
                STEAM_CONTENT=str(root / "content-builds"),
                SCRATCH=str(root / "scratch" / "builds"),
                OUT=str(out_builds),
            ),
        )
        assert builds.returncode == 0, (builds.stdout, builds.stderr)
        assert (out_builds / "parity_fakebuilds.json").is_file(), builds.stdout
        assert "manifest=1633674551820196085" in builds_log.read_text(encoding="utf-8")

        # 4. a steamcmd that silently does nothing must not publish a snapshot
        out_silent = root / "out-silent"
        silent = fetch("1633674551820196085", "fakesilent", "nothing", out_silent, root / "c1")
        assert silent.returncode != 0, silent.stdout
        assert not list(out_silent.glob("parity_*.json")), list(out_silent.iterdir())

        # 5. a failing steamcmd must abort before extraction
        out_fail = root / "out-fail"
        failed = fetch("v3.1.0", "fakefail", "fail", out_fail, root / "content-fail")
        assert failed.returncode != 0, failed.stdout
        assert not out_fail.exists() or not list(out_fail.glob("parity_*.json"))

    print(
        "OK: fetch_version.sh manifest + branch downloads, snapshot equality, and "
        "fail-closed paths hold with a fake steamcmd"
    )


if __name__ == "__main__":
    main()
