# rnd2026 with Heed physics vs legacy physics (2026-10-19)

The geometry and run points are the same in both batches (50 µm mylar stack, 106 jobs). Only the physics differs:

| batch | physics | EOS |
|---|---|---|
| rnd2026_mylar50 (cluster 12550258) | legacy: option4, PIXE on, edep/W in the gas | `/eos/user/a/akallits/p2_sim/rnd2026_mylar50` |
| rnd2026_heed (cluster 12558227) | `--heed --no-pixe --pai config` (commit 6fa7f12) | `/eos/user/a/akallits/p2_sim/rnd2026_heed` |

All 106 heed jobs finished without errors. RunMeta was checked in every file (heed = 1, pixe = 0).

Contents:
- `heed_vs_legacy.csv`: from `scripts/analysis/rnd2026_heed_vs_legacy.py`. For every point, nPrimDrift mean, median, P(n<10) and P(n<5); for photons, P(detected).
- `out_rnd2026_heed/`, `out_rnd2026_mylar50/`: the same `rnd2026_photons_electrons.py` analysis on each batch, including figures, upper cut and P2Sim fold.

## Electrons (100 MeV) and muons: drift-gas primaries

| point (0°) | mean legacy → heed | median | P(n<10) [%] |
|---|---|---|---|
| Ar/iso 95/5, 4 mm | 52.5 → 43.9 (×0.84) | 37 → 30 | 1.19 → 1.89 |
| Ar/iso 95/5, 5 mm | 68.2 → 56.1 (×0.82) | 49 → 39 | 0.17 → 0.13 |
| Ar/iso 90/10, 4 mm | 54.1 → 46.9 (×0.87) | 39 → 32 | 0.76 → 0.75 |
| Ne/iso 95/5, 4 mm | 23.0 → 21.0 (×0.92) | 14 → 14 | 26.1 → 25.7 |
| Ne/iso 85/15, 4 mm | 30.9 → 29.1 (×0.94) | 19 → 19 | 11.4 → 6.7 |
| Ar/CO2/iso, 150 GeV µ | 48.3 → 45.9 (×0.95) | 33 → 30 | 2.21 → 2.29 |

**Electron primaries drop by 13–18 % in argon and 6–13 % in neon.** That is PIXE removed, together with Heed's ionization model.

**The low tail does not simply halve against legacy.** The halving seen on 16 Oct was Heed against PAI with edep/W *without* PIXE. Legacy PIXE had shifted the whole argon spectrum up, which hid part of its low tail.
- Against legacy, the argon 4 mm low tail grows: P(n<10) 1.2 → 1.9 %.
- The neon low tails shrink (Ne/iso 85/15: 11.4 → 6.7 %).

**Muons drop by 5 %.** Geant4 has no muon PIXE, so this is the ionization model alone.

## Photons: unchanged, as expected

- P(≥1 drift primary), heed / legacy, over all 80 photon points: mean 1.017, range 0.89–1.10, within statistics.
- The mean number of primaries in detected events is unchanged.
- Photon electrons are below the Heed thresholds, so this was expected.

## Upper cut (e/γ, edepDrift)

- The detected photon rates per layer are unchanged.
- The rate after the 99 % electron cut changes where the cut lands near the photon peaks. Ar/iso 4 mm, MM0: 40.5 → 54.3 MHz. The cut moves from 9.3 to 10.3 keV, which sits near the 8 keV Cu-K line.
- Elsewhere the change is within ±10 %. This cut is sensitive to its exact position.

**Caveat.** With `--heed`, edepDrift in the gas is Heed's energy loss. Heed's cluster energies are not exactly the same quantity as Geant4's deposit (see `docs/results/heed/pai`). For any electron-count observable, use nPrimDrift / the ClusterTree.
