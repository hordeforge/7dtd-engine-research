#!/usr/bin/env python3
"""Machine-checked XML data pins: key values from the operator's Data/Config.

StockFacts.exe pins DLL constants; this pins selected XML data values that
the corpus and zdtd's provenance register cite (the zombie HP ladder from
entityclasses.xml replace_passive_effect, etc.). Values are pinned against the
installed game so a data change (or wrong claim) fails the gate. Every section
declared in SECTION_SPECS is extracted, committed and diffed by --check: a
section that is extracted and committed but never diffed against the install
would let silent drift pass as a green gate, so the section table is the single
place a new pin site is registered (source file, parser, minimum parsed
values, and the constant keys that section always carries).

Usage:
  python3 tools/xml_pins.py [--pins FILE] --game-dir DIR  # regenerate pins from DIR
  python3 tools/xml_pins.py --check [--pins FILE]         # check committed pins vs the pinned install path
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import tempfile
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tooling

DEFAULT_PINS = str(tooling.TOOLS / "data" / "xml_pins.json")

DEFAULT_GAME = ""  # discovered per run, see default_game_dir()
NO_GAME = "no dedicated server found; pass --game-dir or set ASM/SEVENDTD_ASM/SEVENDTD_DS_DIR"


def default_game_dir() -> str:
    """Install root of the discovered dedicated server, "" when there is none.

    The Linux Steam path used to be baked in here, so a Windows or macOS
    operator had to pass --game-dir on every run while the rest of the tooling
    found the same install by itself.

    A variable naming an install that is not there is a configuration error,
    not an absent install: the caller reports it rather than scanning a
    different one.
    """
    asm = tooling.find_asm()
    root = tooling.game_dir(asm) if asm else None
    return str(root) if root else ""


HEALTH_RE = re.compile(r'name="(health[A-Za-z0-9_]*)"\s*value="([^"]*)"')


def parse_float(text: str, where: str, unparsed: list[str]) -> float | None:
    """A value that is not a plain finite number is a finding, not a crash.

    An install whose markup or threshold carries a locale comma or a stray unit
    must degrade to a named skip that fails the gate closed; float() alone
    raised ValueError and left a traceback with no verdict. float() also accepts
    "nan"/"inf", which no price or threshold ever is: those reach the pins file
    as the non-standard JSON literals NaN/Infinity and never compare equal, so
    --check would report drift on an unchanged install forever.
    """
    try:
        value = float(text)
    except ValueError:
        unparsed.append(f"{where}: {text!r} is not a number")
        return None
    if not math.isfinite(value):
        unparsed.append(f"{where}: {text!r} is not a finite number")
        return None
    return value


def entityclasses_health(text: str, unparsed: list[str]) -> dict[str, int]:
    """health* values inside the replace_passive_effect block.

    A value the gate cannot read is a named skip, not a silently dropped key:
    dropping it would remove a pinned value from the corpus and leave --check
    green against an install that no longer carries it.
    """
    m = re.search(r"<replace_passive_effect>.*?</replace_passive_effect>", text, re.S)
    block = m.group(0) if m else ""
    out: dict[str, int] = {}
    for name, val in HEALTH_RE.findall(block):
        try:
            out[name] = int(val)
        except ValueError:
            unparsed.append(f"entityclasses.xml {name}: {val!r} is not an integer")
    return out


def traders_root(text: str, unparsed: list[str]) -> dict[str, float]:
    """buy_markup / sell_markdown off the <traders> root element."""
    m = re.search(r"<traders\b[^>]*>", text)
    if not m:
        return {}
    found: dict[str, float] = {}
    for attr in ("buy_markup", "sell_markdown"):
        am = re.search(rf'\b{attr}="([^"]+)"', m.group(0))
        if am:
            value = parse_float(am.group(1), f"Data/Config/traders.xml:{attr}", unparsed)
            if value is not None:
                found[attr] = value
    return found


def buffs_survival(text: str, unparsed: list[str]) -> dict[str, float]:
    """Survival thresholds: StatComparePercCurrentToMax on Food/Water."""
    found: dict[str, float] = {}
    for stat in ("Food", "Water"):
        m = re.search(
            rf'StatComparePercCurrentToMax"[^>]*stat="{stat}"[^>]*operation="GT"[^>]*value="([^"]+)"',
            text,
        )
        if m:
            key = f"{stat.lower()}_wellfed_threshold"
            value = parse_float(m.group(1), f"Data/Config/buffs.xml:{key}", unparsed)
            if value is not None:
                found[key] = value
    return found


@dataclass(frozen=True)
class Section:
    """One pinned data section and everything the gate needs to police it.

    `parse` returns the values read out of the install's config file;
    `constants` are the section's stable identity keys, pinned without being
    parsed; `min_parsed` is how many file-derived values must appear before
    regeneration will overwrite the committed section (a renamed config block
    or a wrong --game-dir must fail, not wipe the pins).
    """

    name: str
    config: str
    parse: Callable[[str, list[str]], dict[str, Any]]
    min_parsed: int
    constants: dict[str, Any] = field(default_factory=dict)


# Every pin site, in one table: extraction, --check diffing, the "sources"
# record and the regeneration refusal all read from this list.
SECTION_SPECS: tuple[Section, ...] = (
    Section(
        name="entityclasses_health",
        config="Data/Config/entityclasses.xml",
        parse=entityclasses_health,
        min_parsed=1,
    ),
    Section(
        name="traders_root",
        config="Data/Config/traders.xml",
        parse=traders_root,
        min_parsed=1,
    ),
    Section(
        name="buffs_survival",
        config="Data/Config/buffs.xml",
        parse=buffs_survival,
        min_parsed=1,
        constants={"hunger_buff": "buffStatusHungry01", "thirst_buff": "buffStatusThirsty01"},
    ),
)

SECTIONS = tuple(spec.name for spec in SECTION_SPECS)
SOURCE_FILES = {os.path.basename(spec.config): spec.config for spec in SECTION_SPECS}


def extract(game_dir: str) -> dict[str, Any]:
    unparsed: list[str] = []
    values: dict[str, dict[str, Any]] = {}

    # Source identity: hash of the exact bytes each pinned section was read
    # from. Version labels repeat across silent re-releases; these hashes do
    # not, and --check fails closed when they drift.
    source_identity: dict[str, dict[str, Any]] = {}
    for key, rel in SOURCE_FILES.items():
        path = os.path.join(game_dir, rel)
        if os.path.isfile(path):
            source_identity[key] = {
                "bytes": os.stat(path).st_size,
                "sha256": tooling.sha256_file(Path(path)),
            }

    for spec in SECTION_SPECS:
        path = os.path.join(game_dir, spec.config)
        parsed: dict[str, Any] = {}
        if os.path.isfile(path):
            with open(path, encoding="utf-8", errors="replace") as fh:
                parsed = spec.parse(fh.read(), unparsed)
        values[spec.name] = {**parsed, **spec.constants}

    return {
        "sources": [spec.config for spec in SECTION_SPECS],
        "source_identity": source_identity,
        "unparsed": unparsed,
        **values,
    }


def refusals(data: dict[str, Any], game_dir: str) -> list[str]:
    """Reasons regeneration must not overwrite the committed pins.

    A wrong --game-dir, a renamed config block, or a source file that parses
    to nothing must leave the pins alone rather than replace them with empty
    sections and report success. A source file that is missing entirely is
    the same failure: an incomplete --game-dir would otherwise drop a whole
    section from the pins and still report success.
    """
    out = list(data["unparsed"])
    for spec in SECTION_SPECS:
        path = os.path.join(game_dir, spec.config)
        if not os.path.isfile(path):
            out.append(f"{path} not found; --game-dir is not a dedicated-server install root")
        elif len(data[spec.name]) - len(spec.constants) < spec.min_parsed:
            out.append(
                f"{path} present but no {spec.name} value parsed "
                f"(need {spec.min_parsed}; config section renamed?)"
            )
    return out


def section_diffs(live: dict[str, Any], committed: dict[str, Any]) -> list[str]:
    """Per-key diffs across every pinned section (install value vs committed)."""
    diffs: list[str] = []
    for sec in SECTIONS:
        lv, cv = live.get(sec) or {}, committed.get(sec) or {}
        for k in sorted(set(lv) | set(cv)):
            if lv.get(k) != cv.get(k):
                diffs.append(f"{sec}.{k}: install={lv.get(k)!r} pinned={cv.get(k)!r}")
    return diffs


def identity_diffs(live: dict[str, Any], committed: dict[str, Any]) -> list[str]:
    """Byte-identity diffs for the exact files the pins were read from.

    A silent TFP re-release keeps every pinned value and still changes bytes;
    the hash is what catches it.
    """
    diffs: list[str] = []
    lv, cv = live.get("source_identity") or {}, committed.get("source_identity") or {}
    if not cv:
        return [
            "source_identity: committed pins carry no source hashes (re-run xml_pins.py --game-dir <studied install>)"
        ]
    for key, rel in sorted(SOURCE_FILES.items()):
        want = (cv.get(key) or {}).get("sha256")
        got = (lv.get(key) or {}).get("sha256")
        if not want or not isinstance(want, str) or len(want) != 64:
            diffs.append(f"source_identity.{key}: committed pin has no usable sha256")
        elif got != want:
            diffs.append(
                f"source_identity.{key}: install bytes differ from the studied file "
                f"(install={got!r} pinned={want!r}; {rel})"
            )
    return diffs


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Machine-checked XML data pins: key values from the operator's Data/Config."
    )
    ap.add_argument(
        "--game-dir",
        default=DEFAULT_GAME,
        help="dedicated-server install root (default: the discovered install)",
    )
    ap.add_argument("--check", action="store_true", help="verify committed pins vs the install")
    ap.add_argument(
        "--pins", default=DEFAULT_PINS, help="pins JSON path (default: tools/data/xml_pins.json)"
    )
    args = ap.parse_args()
    pins_path = args.pins
    try:
        game_dir = args.game_dir or default_game_dir()
    except tooling.ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if not game_dir:
        print(f"error: {NO_GAME}", file=sys.stderr)
        return 2

    if not args.check:
        epath = os.path.join(game_dir, SECTION_SPECS[0].config)
        if not os.path.isfile(epath):
            print(
                f"error: {epath} not found; pass the dedicated-server root via --game-dir",
                file=sys.stderr,
            )
            return 2
        data = extract(game_dir)
        # A wrong --game-dir (or a renamed config section) must not wipe the
        # committed pins with empty values while reporting success. Same rule
        # for every section whose source file exists but parses to nothing.
        reasons = refusals(data, game_dir)
        if reasons:
            for r in reasons:
                print(
                    f"error: {r}; refusing to overwrite {pins_path} with empty pins",
                    file=sys.stderr,
                )
            return 2
        pins_dir = os.path.dirname(os.path.abspath(pins_path))
        os.makedirs(pins_dir, exist_ok=True)
        tmp = None
        try:
            with tempfile.NamedTemporaryFile(
                "w", encoding="utf-8", dir=pins_dir, delete=False
            ) as f:
                tmp = f.name
                json.dump(data, f, indent=1, sort_keys=True)
                f.write("\n")
            os.replace(tmp, pins_path)
        finally:
            if tmp and os.path.exists(tmp):
                os.unlink(tmp)
        counts = ", ".join(f"{len(data[spec.name])} {spec.name}" for spec in SECTION_SPECS)
        print(f"wrote {pins_path} ({counts})")
        return 0

    if not os.path.isdir(game_dir):
        print(f"error: game dir not found: {game_dir} (--game-dir)", file=sys.stderr)
        return 2
    live = extract(game_dir)
    if live["unparsed"]:
        # A pinned value the install carries in a shape the gate cannot read is
        # drift the operator has to see, not a value the gate may skip.
        print("FAIL: xml pins: values the gate could not read from the install")
        for u in live["unparsed"]:
            print(f"  - {u}")
        return 1
    if not os.path.isfile(pins_path):
        print(f"FAIL: {pins_path} missing (run xml_pins.py --game-dir first)")
        return 1
    try:
        committed = tooling.load_json(Path(pins_path))
    except (json.JSONDecodeError, OSError, tooling.NonFiniteNumberError) as exc:
        # A corrupt pins file must read as a failed gate (with the repair
        # hint), not as a traceback with no verdict.
        print(f"FAIL: {pins_path}: {exc}")
        print("  regenerate with: python3 tools/xml_pins.py --game-dir <dir>")
        return 1
    diffs = section_diffs(live, committed)
    diffs.extend(identity_diffs(live, committed))
    if diffs:
        print(f"FAIL: xml pins drift from install ({len(diffs)} diffs):")
        for d in diffs:
            print(f"  - {d}")
        return 1
    live_id = live.get("source_identity") or {}
    got = sorted(
        f"{k}={v.get('sha256', '')[:12]}" for k, v in live_id.items() if isinstance(v, dict)
    )
    counts = ", ".join(f"{len(committed.get(spec.name, {}))} {spec.name}" for spec in SECTION_SPECS)
    print(f"OK: xml pins match install ({counts}; sources {', '.join(got)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
