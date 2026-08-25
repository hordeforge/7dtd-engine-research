#!/usr/bin/env python3
"""Dump the uvmapping TextAssets from the meshdescriptions UnityFS bundle.

The atlas XMLs (MeshDescription.MetaData TextAssets) carry the per-texture
`color` that Block.GetColorForSide returns for minimap colors (docs/
texture-atlas.md). This tool extracts them from the operator install's
Data/Addressables/Standalone/meshdescriptions_assets_all.bundle into
tools/sandbox/atlas/*.xml for provenance + regeneration of the zdtd comptime
atlas table. Uses UnityPy (a reference UnityFS/SerializedFile parser).

Usage: python3 extract_mesh_atlas.py <meshdescriptions_assets_all.bundle>

Deps: UnityPy, hash-pinned in requirements.txt next to this script
(uv pip install -r requirements.txt).
"""

import argparse
import os
import tempfile
from pathlib import Path

from safe_name import safe_name

try:
    import UnityPy
except ModuleNotFoundError as exc:
    UnityPy = None
    IMPORT_ERROR = exc
else:
    IMPORT_ERROR = None


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("bundle", type=Path)
    ap.add_argument("--out-dir", type=Path, default=Path(__file__).resolve().parent / "atlas")
    args = ap.parse_args()
    if IMPORT_ERROR:
        ap.error(f"missing dependency {IMPORT_ERROR.name!r}; install sandbox/requirements.txt")

    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    env = UnityPy.load(args.bundle)
    with tempfile.TemporaryDirectory(prefix=".atlas.", dir=out_dir.parent) as td:
        staged = Path(td)
        n = 0
        for f in env.files.values():
            for name, sf in getattr(f, "files", {}).items():
                if not name.startswith("CAB-") or name.endswith("resS"):
                    continue
                for obj in sf.objects.values():
                    if obj.type_id is None or obj.type_id >= len(sf.types):
                        continue
                    if sf.types[obj.type_id].class_id != 49:  # TextAsset
                        continue
                    data = obj.read()
                    target = staged / (safe_name(data.m_Name) + ".xml")
                    if target.exists():
                        raise ValueError(f"duplicate sanitized TextAsset name: {target.name}")
                    script = data.m_Script
                    if isinstance(script, bytes):
                        script = script.decode("utf-8")
                    target.write_text(script, encoding="utf-8")
                    n += 1
        if not n:
            raise ValueError(f"no TextAssets found in {args.bundle}")
        expected = {p.name for p in staged.iterdir()}
        for old in out_dir.glob("*.xml"):
            if old.name not in expected:
                old.unlink()
        for source in staged.iterdir():
            target = out_dir / source.name
            os.replace(source, target)
            print(f"wrote {target} ({target.stat().st_size} bytes)")
    print(f"total TextAssets: {n}")


if __name__ == "__main__":
    main()
