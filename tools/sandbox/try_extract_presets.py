"""Attempt to extract the sandbox_presets TextAsset (the six difficulty
presets, LoadInternalPresets IL=43 Resources.Load("Data/Sandbox/
sandbox_presets")) from the shipped Unity bundles.

Status 2026-08-25: BLOCKED - no sandbox TextAsset found in either install.
resources.resource returns 0 objects under UnityPy 1.25.3; data.unity3d
(8255 objects) holds no TextAsset; Bundles/Addressables/StreamingAssets
hold none either (dedicated catalog is empty). Run with a UnityPy venv:
    python3 -m venv /tmp/uv && /tmp/uv/bin/pip install UnityPy
    /tmp/uv/bin/python tools/sandbox/try_extract_presets.py [game_dir]
Re-run after a game update or with a different bundle extractor; the preset
codes (section 3 codec) would fill the GameDifficulty 0..5 ladder directly.
"""

import os
import sys

import UnityPy


def main() -> int:
    root = (
        sys.argv[1]
        if len(sys.argv) > 1
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
