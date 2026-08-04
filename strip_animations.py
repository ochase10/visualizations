#!/usr/bin/env python
"""Strip embedded to_jshtml() animation players out of notebooks.

A single anim.to_jshtml() output is a base64 blob of every frame -- tens of MB
in one cell. Static figures are left alone, so the notebook still reads fine;
the animations themselves live in assets/ as GIF/MP4.

    python strip_animations.py bao_animation.ipynb
    python strip_animations.py *.ipynb --threshold 512
"""

import argparse
import json
import sys


def strip(path, threshold_kb):
    with open(path) as fh:
        nb = json.load(fh)

    removed = []
    for i, cell in enumerate(nb.get("cells", [])):
        for out in cell.get("outputs", []):
            data = out.get("data", {})
            html = data.get("text/html")
            if html is None:
                continue
            size = len(json.dumps(html))
            if size < threshold_kb * 1024:
                continue
            del data["text/html"]
            data.setdefault("text/plain", ["<animation stripped -- re-run to view>"])
            removed.append((i, size))

    if removed:
        with open(path, "w") as fh:
            json.dump(nb, fh, indent=1)
            fh.write("\n")
    return removed


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("notebooks", nargs="+")
    ap.add_argument("--threshold", type=int, default=512,
                    help="strip text/html outputs larger than this many KB")
    args = ap.parse_args()

    for path in args.notebooks:
        removed = strip(path, args.threshold)
        if not removed:
            print(f"{path}: nothing to strip")
            continue
        total = sum(s for _, s in removed) / 1e6
        cells = ", ".join(str(i) for i, _ in removed)
        print(f"{path}: removed {len(removed)} player(s) from cell {cells} ({total:.1f} MB)")


if __name__ == "__main__":
    sys.exit(main())
