#!/usr/bin/env python3
"""check_local_vs_reference.py — is a locally produced mm_sim file the same
physics as the lxplus production file of the same run point?

    python3 scripts/check_local_vs_reference.py <local.root> <reference.root>

Compares RunMeta (physics switches, geometry hash) and the drift-gas primary
count nPrimDrift as a full distribution: mean, median, P(n<10), P(n<5) and a
two-sample KS test. Used in docs/SETUP.md §4. Exit code 1 if the
geometry or physics settings differ or the KS p-value is below 0.01.
"""
import sys

import numpy as np
import uproot
from scipy import stats

KEYS = ["geometryHash", "gas", "particle", "energy_MeV", "heed", "pixe", "pai",
        "gasStep_um", "driftGap_mm", "beamSpread_mm", "gitHash", "thrown"]
MUST_MATCH = ["geometryHash", "gas", "particle", "energy_MeV", "heed", "pixe",
              "pai", "gasStep_um", "driftGap_mm", "beamSpread_mm"]


def load(path):
    f = uproot.open(path)
    meta = {k: f["RunMeta"][k].array(library="np")[0] for k in KEYS}
    meta = {k: (v.decode() if isinstance(v, bytes) else v) for k, v in meta.items()}
    n = f["EventTree"]["nPrimDrift"].array(library="np")
    return meta, n


def summary(n):
    return dict(N=len(n), mean=n.mean(), median=np.median(n),
                p_lt10=100 * np.mean(n < 10), p_lt5=100 * np.mean(n < 5))


def main(local, ref):
    ml, nl = load(local)
    mr, nr = load(ref)
    ok = True
    print(f"{'RunMeta':16s} {'local':>22s} {'reference':>22s}")
    for k in KEYS:
        same = str(ml[k]) == str(mr[k])
        flag = "" if same or k not in MUST_MATCH else "   <-- DIFFERS"
        if flag:
            ok = False
        print(f"{k:16s} {str(ml[k]):>22s} {str(mr[k]):>22s}{flag}")
    sl, sr = summary(nl), summary(nr)
    print(f"\n{'nPrimDrift':16s} {'local':>10s} {'reference':>10s}")
    for k in sl:
        print(f"{k:16s} {sl[k]:10.3f} {sr[k]:10.3f}")
    ks = stats.ks_2samp(nl, nr)
    print(f"{'KS D / p':16s} {ks.statistic:10.4f} {ks.pvalue:10.3f}")
    if ks.pvalue < 0.01:
        ok = False
    print("\nRESULT:", "same physics (within statistics)" if ok else "DIFFERENT")
    return 0 if ok else 1


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1], sys.argv[2]))
