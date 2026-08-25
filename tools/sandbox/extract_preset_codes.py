#!/usr/bin/env python3
"""Decode the difficulty preset codes from the sandbox_presets TextAsset.

The six GameDifficulty presets (Scavenger..Insane) live in the bundled
TextAsset `Data/Sandbox/sandbox_presets` (SandboxOptionManager.
LoadInternalPresets IL=43 -> Resources.Load). The dedi ships no copy and
the bundles were previously unparseable; the TextAsset is present in the
CLIENT install's data.unity3d and extracts with UnityPy:

    python3 -m venv /tmp/uv && /tmp/uv/bin/pip install UnityPy
    /tmp/uv/bin/python - <<'EOF'
    import UnityPy, os
    env = UnityPy.load(os.path.join(CLIENT, "7DaysToDie_Data", "data.unity3d"))
    for obj in env.objects:
        if obj.type.name != "TextAsset":
            continue
        d = obj.read()
        if (getattr(d, "m_Name", "") or "") == "sandbox_presets":
            s = getattr(d, "m_Script", b"")
            open("sandbox_presets.xml", "wb").write(
                s.encode("utf-8") if isinstance(s, str) else bytes(s))
    EOF

Each preset carries a SandboxCode (sandbox-options.md §3 codec: 'A' +
3-letter groups of base-26 option id + value-set index). Decoding the six
Difficulty-category codes yields the per-difficulty damage modifiers that
feed `ItemActionAttack.difficultyModifier` via
`UpdateInGameValuesWithSandboxOptions` (options 17 IncomingDamage and 42
EntityIncomingDamage).

Usage:
  python3 extract_preset_codes.py [sandbox_presets.xml] [sandbox_tables.json]
"""

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent


def decode(code: str, opts: dict, sets: dict) -> dict:
    out: dict = {}
    if not code:
        return out
    if not code.startswith("A") or (len(code) - 1) % 3:
        raise ValueError(f"invalid sandbox code shape: {code!r}")
    i = 1
    while i < len(code):
        g = code[i : i + 3]
        i += 3
        if not all("A" <= c <= "Z" for c in g):
            raise ValueError(f"invalid sandbox code group: {g!r}")
        oid = (ord(g[0]) - 65) * 26 + (ord(g[1]) - 65)
        idx = ord(g[2]) - 65
        o = opts.get(oid)
        if not o:
            raise ValueError(f"sandbox code references unknown option {oid}")
        vs = sets.get(o["valueset"], {}).get("values", [])
        if idx >= len(vs):
            raise ValueError(f"sandbox option {oid} value index {idx} is out of range")
        out[o["name"]] = vs[idx]
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("xml", nargs="?", type=Path, default=HERE / "sandbox_presets.xml")
    ap.add_argument("tables", nargs="?", type=Path, default=HERE / "sandbox_tables.json")
    args = ap.parse_args()
    with args.tables.open(encoding="utf-8") as fh:
        tables = json.load(fh)
    opts = {o["id"]: o for o in tables["options"]}
    sets = tables["valuesets"]

    root = ET.parse(args.xml).getroot()
    print("preset | code | IncomingDamage | EntityIncomingDamage | RangedDamage | MeleeDamage")
    presets = [p for p in root.findall("preset") if p.get("category") == "Difficulty"]
    if not presets:
        raise ValueError(f"no Difficulty presets found in {args.xml}")
    for preset in presets:
        name, code = preset.get("name", ""), preset.get("code", "")
        dec = decode(code, opts, sets)
        default = {o["name"]: o["default"] for o in opts.values()}
        print(
            f"{name:16s} | {code or '(defaults)'} | "
            f"{dec.get('IncomingDamage', default['IncomingDamage']):g} | "
            f"{dec.get('EntityIncomingDamage', default['EntityIncomingDamage']):g} | "
            f"{dec.get('RangedDamage', default['RangedDamage']):g} | "
            f"{dec.get('MeleeDamage', default['MeleeDamage']):g}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
