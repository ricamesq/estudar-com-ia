"""
VOSviewer JSON → classic .map + .net files (desktop format).

Usage:
    python json_to_map_net.py input.json --out-prefix out
      → writes out.map and out.net
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("json_file")
    ap.add_argument("--out-prefix", default="vosviewer-out/map")
    args = ap.parse_args()

    data = json.loads(Path(args.json_file).read_text(encoding="utf-8"))
    network = data["network"]
    items = network["items"]
    links = network["links"]

    # Build header from unique weight keys
    weight_keys: list[str] = []
    seen: set[str] = set()
    for it in items:
        for k in (it.get("weights") or {}).keys():
            if k not in seen:
                seen.add(k)
                weight_keys.append(k)

    # .map file: tab separated
    map_lines = ["id\tlabel\tcluster\tx\ty\t" + "\t".join(f"weight<{k}>" for k in weight_keys)]
    for it in items:
        row = [
            str(it["id"]),
            (it.get("label") or "").replace("\t", " "),
            str(it.get("cluster", 1)),
            str(it.get("x", 0)),
            str(it.get("y", 0)),
        ]
        w = it.get("weights") or {}
        row.extend(str(w.get(k, 0)) for k in weight_keys)
        map_lines.append("\t".join(row))

    # .net file: source\ttarget\tstrength
    net_lines = []
    for lk in links:
        net_lines.append(f"{lk['source_id']}\t{lk['target_id']}\t{lk.get('strength', 1)}")

    out_prefix = Path(args.out_prefix)
    out_prefix.parent.mkdir(parents=True, exist_ok=True)
    map_path = out_prefix.with_suffix(".map")
    net_path = out_prefix.with_suffix(".net")
    map_path.write_text("\n".join(map_lines) + "\n", encoding="utf-8")
    net_path.write_text("\n".join(net_lines) + "\n", encoding="utf-8")
    print(f"✅ {map_path}\n✅ {net_path}")


if __name__ == "__main__":
    main()
