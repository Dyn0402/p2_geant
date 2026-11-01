# Running the P2 chain on your own machine (no CERN account)

You don't need lxplus, EOS, CVMFS or HTCondor for any part of this repo except
**new COMSOL field solves** (see "What you cannot do locally"). This page
covers installing, getting the data, and checking that your setup reproduces
the published numbers before you change anything.

Tested on: Ubuntu 24.04, x86-64, 12 cores, 14 GB RAM (2026-11-01). It should also work on
macOS (conda-forge builds every package used here for osx-arm64 and osx-64), but that has not been tested.

## 1. Install (≈ 45 min, once; mostly the Garfield++ compile)

You need conda, mamba or micromamba. If you have none of them,
[micromamba](https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html)
is a single binary and needs no admin rights.

```bash
git clone https://github.com/akallitss/P2_Geant_Garfield.git
cd P2_Geant_Garfield
conda env create -f environment.yml        # Geant4 11.2.2, ROOT 6.32, compilers, Python
conda activate p2sim
bash scripts/setup_garfield.sh --build     # Garfield++ @ 927e5c21 + our patch -> ~/garfield/install
source scripts/setup_local.sh              # every new shell, after conda activate
bash scripts/build.sh                      # -> build/mm_sim, with --heed enabled
```

`build.sh` should print `Garfield++ found: ... (--heed enabled)`. If it says
`--heed disabled`, `source scripts/setup_local.sh` was not run after the
Garfield build. Production physics needs `--heed`.

Differences from lxplus:
- Geant4 11.2.2 here, 11.2.1 on lxplus (bug-fix release of the same series).
  Section 4 checks that this makes no difference.
- Garfield++ is the same pinned commit + patch as the transparency and gain runs on lxplus.
  On lxplus, `mm_sim --heed` linked the LCG_106 Garfield, but its Heed gives the same
  spectra as the pin (`docs/results/heed/pai`).

## 2. Data (≈ 9 GB core)

The data that lived on EOS (`/eos/user/a/akallits/p2_sim`) comes as tarballs in a
CERNBox share. Alexandra makes them with `scripts/make_data_bundle.sh` and will send you the
link. Extract everything into one directory:

```bash
export P2_DATA=~/p2_data            # the default; put it in your shell rc if different
mkdir -p $P2_DATA
for f in *.tar; do tar -xf $f -C $P2_DATA; done
sha256sum -c SHA256SUMS             # in the download folder
```

`$P2_DATA` has the same layout as `/eos/user/a/akallits/p2_sim`. **Wherever a doc
or script comment gives an `/eos/user/a/akallits/p2_sim/...` path, use
`$P2_DATA/...`.**

| tarball | size | what |
|---|---|---|
| gas_tables, gas_tables_contam | 2 MB | Magboltz `.gas` files |
| rnd2026_heed | 2.4 GB | the production Geant4 batch |
| cell_gap150 | 6.4 GB | COMSOL field maps of the final mesh cell, 8 drift fields |
| transparency | 0.2 GB | all Garfield transparency outputs |
| condor_transp | 45 MB | geometry-DAG Garfield logs (`TRANSPARENCY`/`GAIN` lines), the input to to-do item 1 |
| optional: cell_nik, cell_vm415, cell_gaps_gap150, rnd2026_mylar50, comsol_model | ~19 GB | validation cell, cosmic cell, gap-scan cells, legacy batch, COMSOL model |

The SPS and cosmic **beam data** are not in the bundle. The simulation work only needs
the extracted products, and those are already in the repo (`docs/results/drift_velocity/`,
`contamination/`, `cosmic/`) or in `P2_basket_analysis`.

## 3. Running things

**Geant4.** `submit_condor_p2.py --local N` runs the same job list as on HTCondor, using the same
wrapper and manifest, on N local processes. Use `--only` to pick jobs and `--scale` to
shrink them:

```bash
python3 scripts/submit_condor_p2.py --scan rnd2026 --dry-run          # list all 106 jobs
python3 scripts/submit_condor_p2.py --scan rnd2026 --local 4 \
    --only ArIso_3p964mm_electron100MeV_th0 --scale 0.1 \
    --outdir $P2_DATA/my_rnd2026 --jobdir $P2_DATA/my_rnd2026_jobs
```

Single runs: `./build/mm_sim -m p2 --heed --no-pixe --pai config -g ArIso -p electron -e 100 -n 1000 -t 1 -o out/test`
(`--heed` is single-threaded, so use `-t 1`).

**Garfield++** (transparency, gain, Heed standalone):

```bash
bash scripts/garfield/run_transparency.sh transp \
    $P2_DATA/comsol/p2_sps/h2mm_sweep_gap150/E625 \
    $P2_DATA/gas_tables/ArIso.gas  $P2_DATA/my_transp/E625_ArIso  1000 1 null
bash scripts/garfield/run_gain.sh $P2_DATA/comsol/p2_sps/h2mm_sweep_gap150/E625 \
    $P2_DATA/gas_tables/ArCO2Iso9352.gas $P2_DATA/my_gain/E625 0.36 20
```

The `null` flag (null-collision steps) is **required** for transparency numbers (see `CLAUDE.md`).

**Stage B, VMM, analysis**: plain Python in the env:
`python3 -m stage_b.selftest`, `python3 -m stage_b.run <stageA.root>`,
`python3 scripts/analysis/<script>.py ...` (input paths are arguments).

**Many jobs.** The `.sub`/`.dag` files in `scripts/garfield/` and `scripts/comsol/`
are HTCondor-only. Locally, loop over the same arguments with `xargs -P` or a
shell loop, or use your lab's batch system. Each Garfield job is one
`run_transparency.sh` / `run_gain.sh` call, and the arguments are in the `.sub` files.

Compute, measured on the test machine (one core):
- 100 MeV e⁻ with Heed: 10 000 events in 18 s.
- 10 / 60 keV photons: 10 000 events in 8–10 s.

The full `rnd2026` batch (106 jobs, 80 M events, almost all photons) is therefore about
20 CPU-hours, or a night on an 8-core machine with `--local 8`. The muon points have not
been timed. Garfield transparency runs at ~0.05 s per electron with null steps (Ar/iso, 625 V/cm), so a
5000-electron production point takes ~5 min. A full 7-field × 6-gas sweep fits in an afternoon.

## 4. Check your setup (do this first)

| check | command | lxplus reference | this machine (2026-11-01) |
|---|---|---|---|
| Stage B self-tests | `python3 -m stage_b.selftest` | all pass | all pass |
| VMM emulator | `python3 vmm/vmm_emulator.py` | smoke test OK | OK |
| Transparency, Ar/iso 95/5, 625 V/cm | `run_transparency.sh` as in §3, n = 1000 | 0.943 (`docs/results/mesh/transparency_sweep_gap150.csv`) | **0.944 ± 0.007**, all losses on wires; 54 s |
| Geant4 + Heed, Ar/iso 4 mm, 100 MeV e⁻, 10k events | below | `$P2_DATA/rnd2026_heed/p2_ArIso_3p964mm_electron100MeV_th0_t0.root` | same geometry hash and physics flags; nPrimDrift mean 44.3 vs 43.9, median 29 vs 30, P(n<10) 1.96 vs 1.89 %, **KS p = 0.13**; 18 s |

The Geant4 check:

```bash
python3 scripts/submit_condor_p2.py --scan rnd2026 --local 1 \
    --only ArIso_3p964mm_electron100MeV_th0 \
    --outdir $P2_DATA/my_rnd2026 --jobdir $P2_DATA/my_rnd2026_jobs
python3 scripts/check_local_vs_reference.py \
    $P2_DATA/my_rnd2026/p2_ArIso_3p964mm_electron100MeV_th0_t0.root \
    $P2_DATA/rnd2026_heed/p2_ArIso_3p964mm_electron100MeV_th0_t0.root
```

It compares RunMeta (geometry hash, physics switches) and the whole `nPrimDrift`
distribution, and prints `RESULT: same physics` or `DIFFERENT`. Also run it on any other
point you reproduce. If the geometry hash differs, the geometry code has changed since the
reference batch (commit 6fa7f12), and the comparison is no longer like-for-like.

## 5. What you cannot do locally

- **New COMSOL field solves.** COMSOL needs a licence. The CERN licence only works on lxplus.
  The existing maps cover the final cell at 8 drift fields, plus the variants in the
  optional bundle. To solve a new geometry you need a COMSOL licence at Saclay (the
  colleague who made the model has one), or Alexandra or someone with lxplus runs
  `scripts/comsol/` for you. The model is `comsol_model.tar`. The parameter meanings are in
  `scripts/comsol/README.md`.
- **Reading the SPS raw data** (`/eos/experiment/ntof/...`, 137 GB per scan). Ask
  for extracted products instead.
