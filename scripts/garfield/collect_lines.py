#!/usr/bin/env python3
"""collect_lines.py — gather the TRANSPARENCY or GAIN result lines printed by
mesh_transparency / mesh_gain job logs into one CSV.

    python3 scripts/garfield/collect_lines.py TRANSPARENCY $P2_DATA/condor_transp/geom_*.out -o geom_transparency.csv
    python3 scripts/garfield/collect_lines.py GAIN $P2_DATA/condor_transp/gain_*.out -o geom_gain.csv

Each line looks like
    TRANSPARENCY gas=ArIso cell=.../h2mm_sweep_g120/E1250 n=3000 micro=0.7210 +- 0.0082 rkf=0.9923 ...
Columns: every key=value (the "+- x" after a value becomes <key>_err), plus
  file   the log it came from
  cell   as printed; cell_tag (e.g. h2mm_sweep_g120) and E_drift (V/cm, from E1250)
"""
import argparse
import csv
import re
import sys
from pathlib import Path

PAIR = re.compile(r"(\w+)=(\S+)(?:\s+\+-\s+(\S+))?")


def parse(line):
    row = {}
    for k, v, err in PAIR.findall(line):
        row[k] = v
        if err:
            row[k + "_err"] = err
    cell = row.get("cell", "")
    parts = Path(cell).parts
    if parts and re.fullmatch(r"E\d+", parts[-1]):
        row["E_drift"] = parts[-1][1:]
        row["cell_tag"] = parts[-2] if len(parts) > 1 else ""
    elif parts:
        row["cell_tag"] = parts[-1]
    return row


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("keyword", choices=["TRANSPARENCY", "GAIN"])
    p.add_argument("logs", nargs="+")
    p.add_argument("-o", "--out", default="-")
    a = p.parse_args()
    rows = []
    for f in a.logs:
        for line in open(f, errors="replace"):
            if line.startswith(a.keyword + " "):
                r = parse(line)
                r["file"] = Path(f).name
                rows.append(r)
    if not rows:
        sys.exit(f"no {a.keyword} lines found")
    keys = []
    for r in rows:
        keys += [k for k in r if k not in keys]
    out = sys.stdout if a.out == "-" else open(a.out, "w", newline="")
    w = csv.DictWriter(out, fieldnames=keys)
    w.writeheader()
    w.writerows(rows)
    if a.out != "-":
        print(f"{len(rows)} rows -> {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
