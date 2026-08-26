"""Scan the shipped Unity bundles for the sandbox_presets TextAsset (the six
difficulty presets, LoadInternalPresets IL=43 Resources.Load("Data/Sandbox/
sandbox_presets")). Walks every .bundle/.unity3d/.resource under the game dir
(dedicated layout 7DaysToDieServer_Data, client fallback 7DaysToDie_Data) and
prints any TextAsset whose name mentions sandbox/preset.

Historical note 2026-08-25: the dedicated install held no such TextAsset
(resources.resource parsed to 0 objects under UnityPy 1.25.3; the dedicated
catalog is empty). The asset was recovered from the CLIENT install's
data.unity3d and is committed as sandbox/sandbox_presets.xml; decode it with
extract_preset_codes.py. This probe stays as a re-scan helper for future game
updates.

Run with the repo's hash-pinned UnityPy (uv pip install -r
tools/sandbox/requirements.txt):
    python3 tools/sandbox/try_extract_presets.py [game_dir]
"""

import argparse
import os
import sys
import tempfile
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Scan the shipped Unity bundles for the sandbox_presets TextAsset "
        "(re-scan helper for future game updates)."
    )
    ap.add_argument(
        "game_dir",
        nargs="?",
        help="game install root (default: the Steam client dir)",
    )
    ap.add_argument("--out", type=Path, help="write the matched TextAsset XML here")
    args = ap.parse_args()

    try:
        import UnityPy
    except ModuleNotFoundError:
        ap.error("missing UnityPy; install tools/sandbox/requirements.txt")

    root = (
        args.game_dir
        if args.game_dir
        else os.path.expanduser("~/.local/share/Steam/steamapps/common/7 Days To Die")
    )
    data_dir = os.path.join(root, "7DaysToDie_Data")
    if not os.path.isdir(data_dir):
        data_dir = os.path.join(root, "7DaysToDieServer_Data")
    targets = [
        os.path.join(data_dir, "Resources", "resources.resource"),
        os.path.join(data_dir, "data.unity3d"),
    ]
    for base in ("Data", data_dir):
        for dp, _, files in os.walk(base):
            for fn in files:
                if fn.endswith((".bundle", ".unity3d", ".resource")):
                    targets.append(os.path.join(dp, fn))
    matches = []
    for p in sorted(set(targets)):
        if not os.path.exists(p):
            continue
        try:
            env = UnityPy.load(p)
        except Exception as exc:
            print(f"skip unreadable bundle {p}: {exc}", file=sys.stderr)
            continue
        for obj in env.objects:
            if obj.type.name != "TextAsset":
                continue
            try:
                d = obj.read()
                name = getattr(d, "m_Name", "") or ""
                if name == "sandbox_presets":
                    text = getattr(d, "m_Script", b"")
                    matches.append(
                        (p, text.encode("utf-8") if isinstance(text, str) else bytes(text))
                    )
            except Exception as exc:
                print(f"skip unreadable TextAsset in {p}: {exc}", file=sys.stderr)
    if len(matches) != 1:
        print(
            f"error: expected one sandbox_presets TextAsset, found {len(matches)}", file=sys.stderr
        )
        return 1
    source, text = matches[0]
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        tmp = None
        try:
            with tempfile.NamedTemporaryFile(dir=args.out.parent, delete=False) as fh:
                fh.write(text)
                tmp = Path(fh.name)
            os.replace(tmp, args.out)
        finally:
            if tmp and tmp.exists():
                tmp.unlink()
        print(f"wrote {args.out} ({len(text)} bytes) from {source}")
    else:
        print(f"found sandbox_presets in {source} ({len(text)} bytes); pass --out to save it")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
