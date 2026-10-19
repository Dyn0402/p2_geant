#!/usr/bin/env python3
"""rnd2026: Heed physics vs legacy physics, drift-gas primaries (2026-10-19).

Same geometry (50 um mylar stack), same run points, two physics settings:
  legacy : /eos/.../rnd2026_mylar50  (option4, PIXE on, edep/W in the gas)
  heed   : /eos/.../rnd2026_heed     (--heed --no-pixe --pai config)
Each file's RunMeta is checked (heed / pixe flags) before use.

Per run point: electrons and muons -> mean, median, P(n<10), P(n<5) of
nPrimDrift (events with no drift ionization added back as zeros); photons ->
P(nPrimDrift >= 1) and the mean nPrimDrift of detected events.

    python3 rnd2026_heed_vs_legacy.py <legacy dir> <heed dir> <out.csv>
"""
import csv
import pathlib
import sys

import numpy as np
import uproot


def load(fn):
    with uproot.open(fn) as f:
        m = f["RunMeta"].arrays(library="np")
        th = int(m["thrown"].sum())
        n = f["EventTree"]["nPrimDrift"].array(library="np")
        heed = int(m["heed"][0]) if "heed" in m else 0
        pixe = int(m["pixe"][0]) if "pixe" in m else 1
    return np.concatenate([n, np.zeros(th - len(n), int)]), th, heed, pixe


def main():
    leg, hd, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]), sys.argv[3]
    rows = []
    for fh in sorted(hd.glob("p2_*_t0.root")):
        fl = leg / fh.name
        if not fl.exists():
            continue
        nh, th, heed, pixe = load(fh)
        nl, tl, heedl, pixel = load(fl)
        assert heed == 1 and pixe == 0, fh
        assert heedl == 0 and pixel == 1, fl
        tag = fh.name.replace("_t0.root", "")
        r = dict(point=tag)
        if "gamma" in tag:
            for k, n, t in (("legacy", nl, tl), ("heed", nh, th)):
                det = n[n > 0]
                r[f"P_det_{k}"] = len(det) / t
                r[f"nmean_det_{k}"] = det.mean() if len(det) else float("nan")
            r["P_det_ratio"] = r["P_det_heed"] / r["P_det_legacy"]
        else:
            for k, n in (("legacy", nl), ("heed", nh)):
                r[f"mean_{k}"] = n.mean()
                r[f"median_{k}"] = float(np.median(n))
                r[f"Plt10_{k}"] = np.mean(n < 10)
                r[f"Plt5_{k}"] = np.mean(n < 5)
            r["mean_ratio"] = r["mean_heed"] / r["mean_legacy"]
        rows.append(r)
        print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()}, flush=True)
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
