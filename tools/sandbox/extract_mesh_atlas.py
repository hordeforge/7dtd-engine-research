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
import os
import sys

import UnityPy
from safe_name import safe_name


def main():
    path = sys.argv[1]
    out_dir = os.path.join(os.path.dirname(__file__), "atlas")
    os.makedirs(out_dir, exist_ok=True)
    env = UnityPy.load(path)
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
                # m_Name comes from the bundle, not the filesystem: sanitize
                # like the C# dumpers (src/IlFmt.cs Safe) so a crafted name
                # cannot escape out_dir or form a parent-path fragment.
                target = os.path.join(out_dir, safe_name(data.m_Name) + ".xml")
                with open(target, "w", encoding="utf-8") as fh:
                    fh.write(data.m_Script)
                n += 1
                print(f"wrote {target} ({len(data.m_Script)} bytes)")
    print(f"total TextAssets: {n}")


if __name__ == "__main__":
    main()
