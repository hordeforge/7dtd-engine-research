#!/usr/bin/env python3
"""Fail if research docs / sibling product pins disagree with tools/data/stock_facts.json.

StockFacts.cs regenerates that JSON from the live Assembly-CSharp.dll. This script
only reads the committed (or just-regenerated) JSON and greps known pin sites.

Usage:
  python3 tools/tests/check_stock_facts.py
  python3 tools/tests/check_stock_facts.py --facts path/to/stock_facts.json
  python3 tools/tests/check_stock_facts.py --require-live   # fail if facts missing;
                            # also re-extract the facts from the local dedicated
                            # DLL (bin/StockFacts.exe) and diff every field, so a
                            # game-build drift cannot pass silently

Exit 0 = in sync (or soft-skip if no facts and not --require-live, or if a
sibling repo directory is entirely absent).
Exit 1 = mismatch.
Exit 2 = usage / missing required facts.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import find_asm

ROOT = Path(__file__).resolve().parents[2]  # 7dtd-engine-research
WS = ROOT.parent  # 7dtd workspace
TOOLS = ROOT / "tools"
DEFAULT_FACTS = TOOLS / "data" / "stock_facts.json"

# Fields that legitimately differ between the committed artifact and a fresh
# extraction without indicating game drift: timestamps, provenance bookkeeping,
# schema metadata. Everything else must match byte-for-value.
VOLATILE_FACT_KEYS = {"extracted_utc", "asm", "generated_by", "schema", "provenance"}

_MISSING = object()


def _diff(left: object, right: object, path: str, into: list[str]) -> None:
    if isinstance(left, dict) and isinstance(right, dict):
        for k in sorted(set(left) | set(right)):
            _diff(left.get(k, _MISSING), right.get(k, _MISSING), f"{path}.{k}" if path else k, into)
    elif left != right:

        def fmt(v):
            return "<absent>" if v is _MISSING else repr(v)

        into.append(f"{path}: live={fmt(left)} committed={fmt(right)}")


def check_live_against_dll(facts: dict, errors: list[str]) -> None:
    """Re-extract stock_facts from the local dedicated DLL and diff every field.

    This is the teeth behind the 'facts match the live dedicated DLL' claim: a
    Steam update (or a stale pin) shows up as a named field diff instead of a
    silent pass or a cryptic downstream census mismatch. Skipped (with a note)
    on machines without the game; FAILs with the build command when the game is
    present but the extractor is not.
    """
    asm = find_asm()
    if asm is None:
        print(
            "SKIP: live DLL not found; facts-vs-DLL comparison skipped "
            "(set ASM=<Assembly-CSharp.dll> to enable)"
        )
        return
    exe = TOOLS / "bin" / "StockFacts.exe"
    mono = shutil.which("mono")
    if not exe.is_file():
        errors.append(
            f"live facts comparison skipped: {exe} missing "
            f"(dedicated DLL found at {asm}; cd tools && ./build.sh --skip-legacy)"
        )
        return
    if mono is None:
        errors.append("live facts comparison skipped: mono not on PATH")
        return
    env = dict(os.environ, MONO_PATH=str(TOOLS / "bin"))
    with tempfile.TemporaryDirectory(prefix="stock-facts-live-") as td:
        out = Path(td) / "live_facts.json"
        try:
            proc = subprocess.run(
                [mono, str(exe), str(asm), str(out)],
                capture_output=True,
                text=True,
                env=env,
                timeout=120,
            )
        except subprocess.TimeoutExpired:
            errors.append("live facts extraction timed out after 120s")
            return
        if proc.returncode != 0 or not out.is_file():
            errors.append("live facts extraction failed: " + (proc.stderr or "").strip()[:400])
            return
        try:
            live = json.loads(out.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"live facts extraction produced invalid JSON: {exc}")
            return

    def strip(d):
        return {k: v for k, v in d.items() if k not in VOLATILE_FACT_KEYS}

    diffs: list[str] = []
    _diff(strip(live), strip(facts), "", diffs)
    if diffs:
        lv = live.get("version") or {}
        cm = facts.get("version") or {}
        errors.append(
            f"committed facts do not match the live DLL: local build "
            f"{lv.get('display')} (b{lv.get('build')}) vs pinned "
            f"{cm.get('display')} (b{cm.get('build')}); {len(diffs)} field(s) differ:"
        )
        errors.extend(diffs[:20])
        if len(diffs) > 20:
            errors.append(f"... and {len(diffs) - 20} more")
        errors.append(
            "after a TFP patch re-sync: ASM=<dll> tools/post-update.sh "
            "(then re-pin docs/siblings); or point ASM at the studied build"
        )


def load_facts(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return ""


def must_contain(label: str, text: str, needle: str, errors: list[str]) -> None:
    if needle not in text:
        errors.append(f"{label}: missing {needle!r}")


def must_match(label: str, text: str, pattern: str, errors: list[str]) -> None:
    if not re.search(pattern, text):
        errors.append(f"{label}: no match for /{pattern}/")


def check_xmls_to_load_inventory(errors: list[str]) -> None:
    """xmlsToLoad list: the WorldStaticData cctor's load names (non-XUi core)
    must match the inventory's XmlName rows exactly."""
    asm = find_asm()
    if asm is None:
        print("SKIP: xmlsToLoad cctor check skipped (dedicated Assembly-CSharp.dll not found)")
        return
    env = dict(os.environ)
    env["MONO_PATH"] = str(TOOLS / "bin")
    proc = subprocess.run(
        ["mono", str(TOOLS / "bin" / "DumpMethod.exe"), str(asm), "WorldStaticData", ".cctor"],
        capture_output=True,
        text=True,
        env=env,
        timeout=60,
    )
    # An extractor failure must not masquerade as an inventory drift: an empty
    # cctor dump would otherwise report "core (0) != inventory core (N)" and
    # send the operator hunting through docs instead of at the tool failure.
    if proc.returncode != 0:
        errors.append(
            "xmlsToLoad: DumpMethod.exe failed (rc="
            f"{proc.returncode}): {(proc.stderr or '').strip()[:400]}"
        )
        return
    if not proc.stdout.strip():
        errors.append(
            "xmlsToLoad: DumpMethod.exe returned no IL for WorldStaticData..cctor "
            "(type renamed or extractor stale?)"
        )
        return
    out = proc.stdout
    cctor_names = re.findall(r"ldc\.i4(?:\.\d+|\.s \d+)\n\s*IL_\w+: ldstr (\w+)", out)
    core = sorted(
        n for n in cctor_names if not n.startswith("loadAction") and not n.startswith("XUi")
    )
    inv = []
    in_table = False
    for line in read(ROOT / "docs" / "inventories" / "xmlsToLoad.md").splitlines():
        if line.strip().startswith("| XmlName"):
            in_table = True
            continue
        if in_table:
            if not line.strip().startswith("|"):
                break
            m = re.match(r"\|\s*`([^`]+)`", line.strip())
            if m:
                inv.append(m.group(1))
    inv_core = sorted(n for n in inv if not n.startswith("XUi"))
    if core != inv_core:
        errors.append(f"xmlsToLoad: cctor core ({len(core)}) != inventory core ({len(inv_core)})")


def check_research(facts: dict, errors: list[str]) -> None:
    v = facts["version"]
    display = v["display"]  # facts-driven, e.g. "V {major}.{minor/10}.{minor%10}"
    major, minor, build = v["major"], v["minor"], v["build"]
    tps = facts["sim"]["constants_ticks_per_second"]
    ydim = facts["chunk"]["block_y_dim"]
    layers = facts["chunk"]["block_layers"]
    npkg = facts["network"]["netpackage_top_level_count"]
    save_ver = facts["save"].get("current_save_version")

    cov = read(ROOT / "docs" / "coverage.md")
    # Pin banner: V X.Y.Z (bN) driven entirely by stock_facts (no fixed version soft path).
    pin_display = display.replace("V ", "")  # strip leading V from facts display
    pin_esc = re.escape(pin_display)
    must_match(
        "docs/coverage.md pin",
        cov,
        rf"V\s*{pin_esc}\s*\(b{build}\)|"
        rf"V\s*\*\*{pin_esc}\s*\(b{build}\)\*\*",
        errors,
    )
    # Fallback: Major/Minor/Build triple or display+build without hard-coded line version.
    if not re.search(
        rf"{pin_esc}.*b{build}|b{build}.*{pin_esc}|"
        rf"Major\s*=\s*{major}.*Minor\s*=\s*{minor}.*Build\s*=\s*{build}",
        cov,
        re.I | re.S,
    ):
        if f"Major={major}" not in cov and f"Minor={minor}" not in cov:
            errors.append(
                f"docs/coverage.md: expected version pin for {display} b{build} "
                f"(Major={major} Minor={minor} Build={build})"
            )

    # Chunk dims
    if str(ydim) not in cov and f"ChunkBlockYDim={ydim}" not in cov:
        # coverage mentions ChunkBlockYDim=256 historically
        must_match(
            "docs/coverage.md YDim", cov, rf"ChunkBlockYDim\s*=\s*{ydim}|YDim.*{ydim}", errors
        )
    if str(layers) not in cov and f"ChunkBlockLayers={layers}" not in cov:
        must_match(
            "docs/coverage.md layers",
            cov,
            rf"ChunkBlockLayers\s*=\s*{layers}|Layers.*{layers}",
            errors,
        )

    # Enum index sizes: EnumGameStats/EnumGamePrefs member counts pin the
    # gamestats-gameprefs inventory; the docs must cite 82 + 317.
    en = facts.get("enums", {})
    if en.get("game_stats_members") != 82:
        errors.append(f"stock_facts enums.game_stats_members={en.get('game_stats_members')} != 82")
    if en.get("game_prefs_members") != 317:
        errors.append(f"stock_facts enums.game_prefs_members={en.get('game_prefs_members')} != 317")
    else:
        must_match(
            "docs/inventories/gamestats-gameprefs.md 82+317",
            read(ROOT / "docs" / "inventories" / "gamestats-gameprefs.md"),
            r"82|317",
            errors,
        )

    # xmlsToLoad list: the WorldStaticData cctor's load names (non-XUi core)
    # must match the inventory's XmlName rows exactly.
    try:
        check_xmls_to_load_inventory(errors)
    except Exception as exc:
        errors.append(f"xmlsToLoad check failed: {exc}")

    # LiteNetLib pins: facts carry the library constants; network.md must
    # document them (protocol 13, MaxPacketSize 1432, PossibleMtu).
    lite = facts.get("litenet", {})
    net = read(ROOT / "docs" / "network.md")
    if net and lite:
        must_match("docs/network.md ProtocolId", net, r"ProtocolId", errors)
        must_match("docs/network.md 1432", net, r"1432", errors)
        must_match("docs/network.md 1024", net, r"1024", errors)

    # XML data pins: the committed hp ladder must carry the key zombie values,
    # and the zdtd divergence register must cite healthSlim 125.
    pins_path = ROOT / "tools" / "data" / "xml_pins.json"
    if pins_path.is_file():
        pins = json.loads(pins_path.read_text(encoding="utf-8"))
        hp = pins.get("entityclasses_health", {})
        for key, val in [
            ("healthSlim", 125),
            ("healthSlimFeral", 500),
            ("healthSlimInfernal", 1600),
        ]:
            if hp.get(key) != val:
                errors.append(f"xml_pins entityclasses_health.{key}={hp.get(key)} != {val}")
        prov = read(WS / "zdtd-server" / "docs" / "PROVENANCE.md")
        if prov:
            must_match("zdtd PROVENANCE healthSlim", prov, r"125", errors)
        tr = pins.get("traders_root", {})
        if abs(tr.get("buy_markup", 0) - 3.0) > 1e-9:
            errors.append(f"xml_pins traders_root.buy_markup={tr.get('buy_markup')} != 3.0")
        if abs(tr.get("sell_markdown", 0) - 0.2) > 1e-9:
            errors.append(f"xml_pins traders_root.sell_markdown={tr.get('sell_markdown')} != 0.2")
        if prov and tr.get("sell_markdown"):
            must_match("zdtd PROVENANCE sell_markdown", prov, r"sell_markdown|SellMarkdown", errors)
        bs = pins.get("buffs_survival", {})
        if abs(bs.get("food_wellfed_threshold", 0) - 0.52) > 1e-9:
            errors.append(
                f"xml_pins buffs food_wellfed_threshold={bs.get('food_wellfed_threshold')} != 0.52"
            )
        if prov and bs.get("hunger_buff"):
            must_match("zdtd PROVENANCE buffStatusHungry", prov, r"buffStatusHungry", errors)

    # WaterLevel pin: facts must carry the IL-verified value and save-region.md
    # must document it (the zdtd divergence register consumes the same number).
    water = facts["behaviour"].get("world_water_level")
    if water is None:
        errors.append("stock_facts behaviour.world_water_level missing")
    elif abs(float(water) - 62.88) > 1e-6:
        errors.append(f"stock_facts world_water_level={water} != 62.88 (Block.cWaterLevel)")
    else:
        must_match(
            "docs/save-region.md WaterLevel",
            read(ROOT / "docs" / "save-region.md"),
            r"62\.88",
            errors,
        )

    # Death-loot lifetime + per-frame load budget (cctor-pinned IL values).
    for key, val, doc, pat, label in [
        (
            "item_dropped_on_death_lifetime_s",
            300.0,
            "docs/combat-damage.md",
            r"300",
            "item lifetime",
        ),
        ("max_load_time_per_frame_ms", 50, "docs/crafting-recipes.md", r"50", "load budget"),
    ]:
        got = facts["behaviour"].get(key)
        if got is None:
            errors.append(f"stock_facts behaviour.{key} missing")
        elif abs(float(got) - val) > 1e-6:
            errors.append(f"stock_facts {key}={got} != {val}")
        else:
            must_match(f"docs pin {label}", read(ROOT / doc), pat, errors)

    closed = read(ROOT / "docs" / "closed-gaps.md")
    must_match(
        "docs/closed-gaps.md GameTimer",
        closed,
        rf"ticksPerSecond\s*=\s*\*\*{tps}\*\*|GameTimer\({tps}|ticksPerSecond.*{tps}",
        errors,
    )

    proto = read(ROOT / "docs" / "protocol.md")
    must_contain("docs/protocol.md challenge", proto, "0xCA", errors)
    must_match(
        "docs/protocol.md version display",
        proto,
        re.escape(display) + r"|" + re.escape("V " + pin_display),
        errors,
    )

    if save_ver is not None:
        save = read(ROOT / "docs" / "save-region.md")
        must_match(
            "docs/save-region.md CurrentSaveVersion",
            save,
            rf"CurrentSaveVersion[`\s]*=?\s*\*\*{save_ver}\*\*|CurrentSaveVersion\s*=\s*{save_ver}",
            errors,
        )

    # NetPackage count in coverage/protocol family
    if str(npkg) not in cov and str(npkg) not in proto:
        inv = read(ROOT / "docs" / "protocol-packages.md")
        if str(npkg) not in inv:
            errors.append(
                f"research docs: NetPackage count {npkg} not mentioned in coverage/protocol/protocol-packages"
            )

    # Live census table under coverage.md must not keep V3.0.1 counts as "live"
    census = facts.get("census") or {}
    top = census.get("top_level_types")
    methods = census.get("methods_with_body_top_level")
    saveload = facts.get("save", {}).get("worldstate_saveload_stream_il")
    if top is not None:
        must_match(
            "docs/coverage.md live top-level types",
            cov,
            rf"Top-level types\s*\|\s*{top}\b",
            errors,
        )
    if methods is not None:
        must_match(
            "docs/coverage.md live methods with body",
            cov,
            rf"Methods with body\s*\|\s*{methods}\b",
            errors,
        )
    if saveload is not None:
        must_match(
            "docs/coverage.md live SaveLoad IL",
            cov,
            rf"WorldState\.SaveLoad\(Stream\)\s*IL\s*\|\s*{saveload}\b",
            errors,
        )

    # README must pin current display version (not a stale prior-line banner)
    readme = read(ROOT / "README.md")
    must_match(
        "README.md version pin",
        readme,
        rf"V\s*\*\*{re.escape(pin_display)}\s*\(b{build}\)\*\*|"
        rf"V\s*{re.escape(pin_display)}\s*\(b{build}\)|"
        rf"\(V\s*\*\*{re.escape(pin_display)}",
        errors,
    )

    # TE package layout: V3.1+ must document teBlockId + i32 payload length
    te = facts.get("tile_entity_package") or {}
    if te.get("payload_len_likely_i32") or te.get("present"):
        te_doc = read(ROOT / "docs" / "tile-entities-power.md")
        pkg_doc = read(ROOT / "docs" / "protocol-packages.md")
        must_match(
            "docs/tile-entities-power.md teBlockId",
            te_doc,
            r"teBlockId\s*:\s*i32",
            errors,
        )
        must_match(
            "docs/tile-entities-power.md payloadLen i32",
            te_doc,
            r"payloadLen\s*:\s*i32",
            errors,
        )
        # Stale V3.0.1-only layout block (u16 length, no teBlockId in the same fence)
        if re.search(
            r"```text\s*\nhandle\s*:\s*u8[^`]*payloadLen\s*:\s*u16",
            te_doc,
            re.M,
        ):
            errors.append(
                "docs/tile-entities-power.md: stale NetPackageTileEntity layout "
                "(payloadLen:u16 without V3.1 teBlockId/i32)"
            )
        must_match(
            "docs/protocol-packages.md §6.12 teBlockId",
            pkg_doc,
            r"teBlockId\s*:\s*i32",
            errors,
        )
        must_match(
            "docs/protocol-packages.md §6.12 payloadLen i32",
            pkg_doc,
            r"payloadLen\s*:\s*i32",
            errors,
        )


def check_loadgen(facts: dict, errors: list[str]) -> str | None:
    """Check loadgen pins; return a skip note when the sibling repo is absent."""
    proj = WS / "7dtd-loadgen"
    path = proj / "src" / "LoadGen" / "PackageCodec.cs"
    text = read(path)
    if not text:
        if not proj.is_dir():
            return f"sibling repo absent, loadgen pins skipped: {proj}"
        errors.append(f"loadgen missing: {path}")
        return None
    v = facts["version"]
    # GameVersion = new(1, 3, 10, 14)
    pat = rf"GameVersion\s*=\s*new\s*\(\s*{v['release_type']}\s*,\s*{v['major']}\s*,\s*{v['minor']}\s*,\s*{v['build']}\s*\)"
    must_match("loadgen PackageCodec.GameVersion", text, pat, errors)
    if "0xCA" not in text and "202" not in text:
        # ChallengeChannelMarker = 202
        must_match("loadgen challenge", text, r"ChallengeChannelMarker\s*=\s*202|0xCA", errors)
    return None


def check_zdtd(facts: dict, errors: list[str]) -> str | None:
    """Check zdtd pins; return a skip note when the sibling repo is absent."""
    proj = WS / "zdtd-server"
    ver_path = proj / "src" / "version.zig"
    proto_path = proj / "src" / "protocol.zig"
    ver = read(ver_path)
    proto = read(proto_path)
    if not ver:
        if not proj.is_dir():
            return f"sibling repo absent, zdtd pins skipped: {proj}"
        errors.append(f"zdtd missing: {ver_path}")
        return None
    stock = facts["version"]["stock_wire"]
    must_match(
        "zdtd stock_wire",
        ver,
        rf'pub const stock_wire = "{re.escape(stock)}";',
        errors,
    )
    if not proto:
        errors.append(f"zdtd missing: {proto_path}")
        return None
    tps = facts["sim"]["constants_ticks_per_second"]
    must_match(
        "zdtd ticks_per_second",
        proto,
        rf"pub const ticks_per_second: u32 = {tps};",
        errors,
    )
    ch = facts["network"]["challenge_marker"]
    must_match(
        "zdtd challenge_marker",
        proto,
        rf"pub const challenge_marker: u8 = 0x{ch:02X};|pub const challenge_marker: u8 = {ch};",
        errors,
    )
    ydim = facts["chunk"]["block_y_dim"]
    store = read(WS / "zdtd-server" / "src" / "world" / "store.zig")
    if store:
        must_match("zdtd y_dim", store, rf"pub const y_dim: i32 = {ydim};", errors)
    # LiteNetLib wire pins: facts carry the library constants; zdtd's packet.zig
    # must acknowledge the max_packet_size divergence (1327 vs stock 1432).
    lite = facts.get("litenet", {})
    if lite.get("max_packet_size") != 1432:
        errors.append(f"stock_facts litenet.max_packet_size={lite.get('max_packet_size')} != 1432")
    if lite.get("protocol_id") != 13:
        errors.append(f"stock_facts litenet.protocol_id={lite.get('protocol_id')} != 13")
    pkt = read(WS / "zdtd-server" / "src" / "litenet" / "packet.zig")
    if pkt and lite.get("max_packet_size"):
        must_match(
            "zdtd packet.zig max_packet_size divergence",
            pkt,
            r"1432",
            errors,
        )
    # Cross-repo: the divergence register must carry the machine-checked
    # WaterLevel so zdtd's sea_level=64 divergence stays tied to the pin.
    water = facts["behaviour"].get("world_water_level")
    prov = read(WS / "zdtd-server" / "docs" / "PROVENANCE.md")
    if water is not None and prov:
        must_match(
            "zdtd PROVENANCE WaterLevel register",
            prov,
            r"62\.88",
            errors,
        )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--facts", type=Path, default=DEFAULT_FACTS)
    ap.add_argument(
        "--require-live",
        action="store_true",
        help="fail if stock_facts.json is missing (default: soft-skip)",
    )
    ap.add_argument("--skip-siblings", action="store_true", help="only check research docs")
    args = ap.parse_args()

    if not args.facts.is_file():
        msg = f"stock_facts.json not found at {args.facts}"
        if args.require_live:
            print(f"FAIL: {msg}", file=sys.stderr)
            print("  regenerate: tools/stock-sync.sh", file=sys.stderr)
            return 2
        print(f"SKIP: {msg} (run tools/stock-sync.sh to enable pin gate)")
        return 0

    facts = load_facts(args.facts)
    errors: list[str] = []
    skips: list[str] = []

    # The documented contract for --require-live: the facts under test match the
    # live dedicated DLL (skipped with a note where there is no local game).
    if args.require_live:
        check_live_against_dll(facts, errors)

    # A value under provenance.baked was published as a hard-coded default
    # because IL extraction failed; it must never pass as a verified pin.
    baked = (facts.get("provenance") or {}).get("baked") or []
    for name in baked:
        errors.append(
            f"stock_facts {name} is a baked default, not extracted from the DLL "
            "(re-run tools/stock-sync.sh against the live game, or verify the "
            "value by hand and update StockFacts.cs extraction)"
        )

    check_research(facts, errors)
    if not args.skip_siblings:
        for check in (check_loadgen, check_zdtd):
            note = check(facts, errors)
            if note:
                skips.append(note)

    v = facts["version"]
    print(
        f"stock_facts: {v['display']} (b{v['build']}) "
        f"tps={facts['sim']['constants_ticks_per_second']} "
        f"netpkg={facts['network']['netpackage_top_level_count']} "
        f"ydim={facts['chunk']['block_y_dim']}"
    )
    for s in skips:
        print(f"SKIP: {s}")
    if errors:
        print(f"FAIL: {len(errors)} pin mismatch(es)")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("OK: research + available sibling pins match stock_facts.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
