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


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Scan the shipped Unity bundles for the sandbox_presets TextAsset "
        "(re-scan helper for future game updates)."
    )
    ap.add_argument(
        "game_dir",
        nargs="?",
        help="game install root (default: the Steam dedicated-server dir)",
    )
    args = ap.parse_args()

    import UnityPy

    root = (
        args.game_dir
        if args.game_dir
        else os.path.expanduser(
            "~/.local/share/Steam/steamapps/common/7 Days to Die Dedicated Server"
        )
    )
    data_dir = os.path.join(root, "7DaysToDieServer_Data")
    if not os.path.isdir(data_dir):
        data_dir = os.path.join(root, "7DaysToDie_Data")
    targets = [
        os.path.join(data_dir, "Resources", "resources.resource"),
        os.path.join(data_dir, "data.unity3d"),
    ]
    for base in ("Data", data_dir):
        for dp, _, files in os.walk(base):
            for fn in files:
                if fn.endswith((".bundle", ".unity3d", ".resource")):
                    targets.append(os.path.join(dp, fn))
    seen = 0
    for p in targets:
        if not os.path.exists(p):
            continue
        try:
            env = UnityPy.load(p)
        except Exception as exc:
            print("load fail", p, exc)
            continue
        for obj in env.objects:
            if obj.type.name != "TextAsset":
                continue
            seen += 1
            try:
                d = obj.read()
                name = getattr(d, "m_Name", "") or ""
                if "sandbox" in name.lower() or "preset" in name.lower():
                    text = bytes(d.m_Script) if hasattr(d, "m_Script") else b""
                    print("=== TextAsset:", name, "in", p, "len", len(text))
                    print(text.decode("utf-8", "replace")[:2000])
            except Exception:
                pass
    print("textassets seen:", seen, "- presets found:", "no" if seen == 0 else "maybe above")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
