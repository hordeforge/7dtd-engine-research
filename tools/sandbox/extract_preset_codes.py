#!/usr/bin/env python3
"""Decode the difficulty preset codes from the sandbox_presets TextAsset.

The six GameDifficulty presets (Scavenger..Insane) live in the bundled
TextAsset `Data/Sandbox/sandbox_presets` (SandboxOptionManager.
LoadInternalPresets IL=43 -> Resources.Load). The dedi ships no copy; the
TextAsset is present in the CLIENT install's data.unity3d, and the committed
sandbox/sandbox_presets.xml is re-extracted from there with:

    python3 tools/sandbox/try_extract_presets.py <client_dir> \
        --out tools/sandbox/sandbox_presets.xml

Each preset carries a SandboxCode (sandbox-options.md §3 codec: 'A' +
3-letter groups of base-26 option id + value-set index). Decoding the six
Difficulty-category codes yields the per-difficulty damage modifiers that
feed `ItemActionAttack.difficultyModifier` via
`UpdateInGameValuesWithSandboxOptions` (options 17 IncomingDamage and 42
EntityIncomingDamage).

Usage:
  python3 extract_preset_codes.py [sandbox_presets.xml] [sandbox_tables.json]

Exit 0 = the six presets decoded; 1 = a preset code is malformed; 2 = usage
error, including a path that is not a readable file.
"""

import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import tooling

HERE = Path(__file__).resolve().parent


def decode(
    code: str, opts: dict[int, dict[str, Any]], sets: dict[str, dict[str, Any]]
) -> dict[str, float]:
    out: dict[str, float] = {}
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
        # The tables are a committed JSON artifact, but a hand-edited or
        # partially regenerated one reaches here as arbitrary data, so every
        # field the codec indexes into is checked before it is indexed: a
        # missing key or a `values` that is not a list is a named refusal,
        # not a KeyError or a TypeError out of the tool.
        if "valueset" not in o or "name" not in o:
            raise ValueError(f"sandbox option {oid} has no valueset/name entry: {o!r}")
        entry = sets.get(o["valueset"]) or {}
        vs = entry.get("values")
        if vs is None:
            # A bool value set carries no table: the index is the bool
            # (sandbox-options.md 2.1 renders YesNo as "false/true").
            if entry.get("type") != "bool":
                raise ValueError(
                    f"sandbox option {oid} value set {o['valueset']!r} has no values "
                    f"and is not a bool set"
                )
            vs = [False, True]
        if not isinstance(vs, list):
            raise ValueError(
                f"sandbox option {oid} value set {o['valueset']!r} values is not a list: {vs!r}"
            )
        if idx >= len(vs):
            raise ValueError(f"sandbox option {oid} value index {idx} is out of range")
        out[o["name"]] = vs[idx]
    return out


def fail(message: str) -> int:
    """Refuse an input the tool cannot act on: plain stderr, exit 2.

    The parser is already built, so this cannot use ap.error(); a usage error
    still exits 2 either way, which is what callers and the gate check for.
    """
    print(f"extract_preset_codes: {message}", file=sys.stderr)
    return 2


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "xml",
        nargs="?",
        type=Path,
        default=HERE / "sandbox_presets.xml",
        help="sandbox_presets TextAsset XML (default: sandbox/sandbox_presets.xml next to this script)",
    )
    ap.add_argument(
        "tables",
        nargs="?",
        type=Path,
        default=HERE / "sandbox_tables.json",
        help="option/value-set tables (default: sandbox/sandbox_tables.json next to this script)",
    )
    args = ap.parse_args(argv)
    for label, path in (("xml", args.xml), ("tables", args.tables)):
        if not path.is_file():
            return fail(f"{label} is not a file: {path}")
    tables = tooling.load_json(args.tables)
    opts = {o["id"]: o for o in tables["options"]}
    sets = tables["valuesets"]

    try:
        root = ET.parse(args.xml).getroot()
    except ET.ParseError as exc:
        return fail(f"xml is not well-formed: {args.xml}: {exc}")
    presets = [p for p in root.findall("preset") if p.get("category") == "Difficulty"]
    if not presets:
        return fail(f"no Difficulty presets found in {args.xml}")
    # Header last: a run that fails must leave stdout empty, so a redirected
    # report is never a bare column header with no rows under it.
    print("preset | code | IncomingDamage | EntityIncomingDamage | RangedDamage | MeleeDamage")
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
    sys.exit(main(sys.argv[1:]))
