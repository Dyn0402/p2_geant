# Handover — P2 Micromegas simulation

**Written:** 2026-11-01 by Alexandra Kallitsopoulou (CEA Saclay), for the PhD
student taking over this work.
**State as of:** last physics commit 7c24ff0 (2026-10-19); status checked 2026-10-21.

This is the document to read first. `HANDOFF.md` and `SIM_CAMPAIGN_BRIEF.md`
are from August 2026 and are kept for history only: their status sections
are out of date. The rules for working in this repo are in `CLAUDE.md` at the
top level. Read them too, because they are the reason the results below can be trusted.
To install and run everything on your own machine (no CERN account needed),
see `docs/LOCAL_SETUP.md`.

---

## 1. What the project is for

P2 at MESA (Mainz) uses wedge-shaped Micromegas with 1280 pads, read out by
VMM3a. At the July 2026 SPS test the VMM saw **85.3 %** efficiency, compared with
**95.6 % for DREAM** on the same pads. The chamber gain varies by about ×3.9 across the
plane (non-planarity), so low-gain pads fall below the VMM threshold.

**The campaign goal** (restated 2026-10-15): find ways to **raise the gas gain**
to make up for the VMM threshold loss. Candidates are isobutane 5 → 10 %,
drift gap 4 → 5 mm and Ne/iso. Higher gain must still give
- (a) per-pad time resolution **≲ 20 ns**;
- (b) e/γ separation. This is nice to have. The background and interaction rates
  are Matthieu Gailliard's study (P2Sim), and this repo only uses his photon spectra as input.

The VMM threshold itself is being lowered separately in lab tests.

Particles: the P2 signal is **100 MeV electrons**. The background is **photons** in the
`BkgHistograms.root` energy range (mostly 40–100 keV). The SPS case
(150 GeV muons) is only used as a validation anchor against data.

## 2. The chain and where each part stands

```
Geant4 (mm_sim, p2 mode)     ->  Stage B (stage_b/)            ->  VMM emulator (vmm/)
 beam/background -> clusters      drift, transparency, gain,         threshold, timing,
 in the drift gas (Heed)           induction -> per-pad q, t          efficiency
 + COMSOL mesh cell -> Garfield++ transparency and gain (scripts/comsol, scripts/garfield)
```

| part | state |
|---|---|
| Geometry (`src/DetectorConstruction.cc`) | Built from the design files. Every number is cited in `docs/P2_GEOMETRY.md`. 50 µm mylar everywhere since 2026-10-15 (commits e745b36, 05dd2a5). |
| Drift-gas ionization | **Heed coupled into Geant4** (`--heed`, `src/HeedGasModel.cc`). Validated against standalone Heed (KS 0.003). This is the production default: `submit_condor_p2.py --physics heed`. |
| Magboltz gas tables | 6 dry mixtures plus contaminated variants. Loaded by Stage B. |
| Mesh transparency (Garfield++) | Final, reviewed and validated against Nikolopoulos et al. (cold gas only). See §4. |
| Gain (Garfield++, `mesh_gain.cc`) | Penning r fitted to data: r ≈ 0.36. See §5. |
| Stage B | Runs end to end. **Transparency and pillar losses are not yet in it** (transparency is still the constant 1.0). |
| VMM emulator | Runs standalone. **It has not yet been run on Stage B output from the Heed batch.** |

## 3. Production samples

Paths are on EOS. Locally they are under `$P2_DATA` (`docs/LOCAL_SETUP.md`).

| batch | physics | where | use? |
|---|---|---|---|
| `rnd2026` (cluster 12403408) | legacy, 10/120 µm mylar | `/eos/user/a/akallits/p2_sim/rnd2026` | **No**: wrong mylar, PIXE bias |
| `rnd2026_mylar50` (12550258) | legacy (option4, PIXE on) | `.../p2_sim/rnd2026_mylar50` | **No** for primaries (PIXE double-counts) |
| **`rnd2026_heed` (12558227)** | `--heed --no-pixe --pai config` | `.../p2_sim/rnd2026_heed` | **Yes**. Always check RunMeta `heed=1`, `pixe=0` |

Results: `docs/results/rnd2026_heed/README.md`. Main point: compared with legacy, the
e⁻ primaries go down by 13–18 % (Ar), and **the Ar 4 mm low tail grows** (P(n<10) goes from 1.2 to 1.9 %),
because PIXE had been hiding it. The low tail is what sets the VMM inefficiency.

## 4. Mesh transparency: final numbers and the method that must be used

SPS point: mesh −450 V, drift 625 V/cm, measured mesh (18 µm wire, 50 µm opening,
68 µm pitch, calendered model). Details are in `docs/results/mesh/README.md`.

| gas | T |
|---|---|
| Ar/iso 95/5 | 94.3 % |
| Ar/iso 90/10 | 99.2 % |
| Ne/iso 95/5 | 93.8 % |
| Ne/iso 85/15 | 99.9 % |
| Ar/CO2/iso 93/5/2 | 97.5 % (0.4 % attachment) |
| Ar/CF4/iso 88/10/2 | 95.5 % (4.5 % CF4 attachment) |

Physics: field lines alone give 100 %. The losses come from diffusion onto the tops of the
wires in the last ~50 µm, and they scale with the electron characteristic energy
ε_k = D_T²E/2 (hot Ar/Ne mixes lose, isobutane cools).

**Every Garfield run must keep these settings.** The first-pass numbers were wrong
without them (Ar/iso 95/5 came out as 90.6 % instead of 94.3 %):
- `aval.EnableNullCollisionSteps(true)`. Without it, wire losses roughly double in hot gases.
- `fm.EnableInterfaceCrossings()` after setting the periodicities, **with our patch**
  `scripts/garfield/patches/interfacepanels_periodic_leaf.patch`. Without the patch
  you get ~50 % fake losses at the cell faces.
- Classify losses by status (−5 = wire, −7 = attachment). Never count
  attachment as a mesh loss.
- COMSOL `meshHeight` is the **wire-centre plane**, not the gap. Use 164.85 µm
  (150 + 1.5·rCut) so the mesh sits on the 150 µm pillars.

## 5. The open problem: the transparency edge

**Not resolved.** Simulated transparency starts to fall **~150–200 V/cm too
early** compared with data:
- SPS `drift_mesh_scan_1` (Ar/CO2/iso 93/5/2, mesh 450 V): at 1125 V/cm, data 0.85 vs
  sim 0.77.
- Cosmic det1 (Ar/iso 95/5, mesh 415 V): still 0.77 at 1375 V/cm.
- The SPS data also lose signal **below 500 V/cm**, where T = 1. SPS relative yield vs field:
  1000: 1.00, 750: 0.93, 625: 0.82, 500: 0.63, 375: 0.36, 250: 0.15.

What is known:
- **Contamination fit** (`scripts/analysis/sps_contamination_fit.py`,
  `docs/results/contamination/`): an O2-like attachment × T × 180 ns shaping
  fits the *whole* SPS scan once a low-field loss is allowed. Most of the
  "edge too early" then goes away, because the earlier max-normalisation was biased.
  But the fit needs ~2000–4600 ppm O2-equivalent, which is implausible and different
  per chamber. Not proven.
- Charging of the drift foil is excluded (data session, 2026-10-16;
  `../P2_basket_analysis/RESULTS_gap_timing.md`).
- Gas tables agree with ILC-TPC to within 5 %, so the problem is not the Magboltz tables.
- A bent or non-planar PCB is a candidate, but **it must be shown in data,
  not assumed**.

**Gain status** (`docs/results/gain/`): DREAM calibration 18 ADC/fC (200 fC
range). Penning r = 0.36 (0.33–0.39) for Ar/CO2/iso and 0.35 for Ar/iso. Open: the
simulated gain e-folding is 31–35 V at every gap, but the data give 22–28 V. Absolute
gain cannot tell you the gap size.

**Geometry DAG 12548862 has finished but has NOT been compared to data.** It covers gaps 120/135/165 µm,
wire Ø16/20 µm, spacings 66/73 µm, a 415 V cosmic variant and 430/470 V ×
4 gaps, giving 121 transparency results and 33 gain results. The transparency outputs are the
`TRANSPARENCY` lines in `condor_transp/geom_<tag>_E<E>_<gas>.out`, which are in the data bundle as
`$P2_DATA/condor_transp/` (from `~/P2_Geant_Garfield/condor_transp` on lxplus). Copy the numbers into
`docs/results/` first.

## 6. To-do list, in priority order

1. **Geometry vs data** (the next step). Plot T(E) for every DAG variation on the
   SPS scan (450 V, ArCO2Iso9352) and the cosmic det1 scan (`_vm415`, ArIso).
   Do it with a free scale *and* with the low-field loss modelled as in the
   contamination fit, not max-normalised. Question: can any plausible geometry
   move the edge by 150–200 V/cm?
2. **Attachment fit to the SPS yield curve** (§5 numbers): data-session request (c).
3. The same contamination-style fit on the **cosmic det1 scan**. That scan has little low-field loss,
   but it still falls at high field, so it is the cross-check of the normalisation explanation.
4. Data-session requests (a) and (b), at cosmic conditions (Ar/iso 95/5, 4 mm):
   - (a) the frac30/peak timing shift for an amplification-gap change, and whether −21 / −11 ns per
     e-fold come out;
   - (b) a gain-vs-gap table at 420 V, to convert std ln G = 0.269 into σ_gap.
5. (d) Cosmic 125 V/cm (+120 ns, σ 82 ns) vs Magboltz v_d and diffusion.
6. **Efficiency chain:** put T (wire losses only) and pillar losses into Stage B,
   then run Stage B → VMM on `rnd2026_heed`, then VMM efficiency vs gain for the
   rnd2026 options. This is the deliverable the campaign is for.
7. Gain-slope mismatch: try a field-dependent Penning r, and check the SPS MPV near
   threshold.
8. Smaller items:
   - The Geant4 mesh default is still 45/63 µm (`include/SimConfig.hh`,
     `p2_mesh_open_um`), but the measured mesh is 50/68 µm. Switch it, and note it in RunMeta.
   - W-value table: ours vs Garfield's (iso 26.0 vs 23.4 eV).
   - Report the interface-crossing bug upstream to Garfield++ (with the patch).
   - Logbook "Next" slide item 1 still says "(needs DREAM fC/ADC)". That is out of date; the calibration is used.

**Validation plan** (agreed 2026-10-15, one stage at a time):
1. v_d from SPS hit times. Done: agrees at ≥ 625 V/cm; data are slower at
   250–500 V/cm, cause open. See `docs/results/drift_velocity/`.
2. Fe55 spectrum and gain slope on the cosmic bench.
3. SPS MIP spectrum and pads per hit through the chain.
4. SPS timing through Stage B → VMM.
5. Drift scans plus a gas-flow scan.

**Still waiting on detector inputs:** whether the mesh is calendered and its thickness; the SPS HV-scan
run list; overpressure (mbar); the 5 mm frame drawing; the beam current behind
Matthieu's MHz rates.

## 7. Data: where it is and the traps

- **SPS July 2026.** Analysis repo `../P2_basket_analysis/sps_beam_analysis/`,
  raw data at `/eos/experiment/ntof/data/x17/p2_sps_july/runs/`.
  - **Take the gas only from the corrected `run_config.json`** (fields `gas`, `gas_note`). Do
    not use the beam logbook or the DAQ config, because they are wrong:
    - runs ≤ 58: **Ar/CO2/iso 93/5/2**
    - runs 59–72: **Ar/CF4/iso 88/10/2**
    - **There was no Ar/iso 95/5 at SPS.** A wrong gas once put the wrong simulation on a slide.
  - DREAM runs: drift/mesh 700/450 V (P2_IN 700/490). VMM runs: 750/450 V.
  - DREAM shaping is 180 ns, 60 ns sampling. Drift field = (V_drift − 450)/0.4 cm.
  - The `28_timing_qa` mean_ns has no amplitude cut, so noise pulls it at low field. Use
    `scripts/analysis/sps_hit_times_extract.py` instead.
- **Cosmic bench (Ar/iso 95/5)** has separate analysis code:
  `../P2_basket_analysis/cosmic_bench_analysis`. Data is on the LaCie disk under `data/Cosmic_Bench`.
- **Design files:** `../Detector_Drawings/` (PCB: `Version_Apr26/FABRICATION_P2`;
  gas frame: `DRIFT_P2_261124/.../FRAME_4mm` STEP; pillars: Insulation_masks V1
  for det1–4, V3B_final for production). The repo copies are in `design/`.
- **Background input:** `../data/Simulations/background_mattieu_data/BkgHistograms.root`.
  Per layer MM0–2: x = E [MeV], y = θ [deg], z = rate [MHz]. Matthieu's own
  geometry (P2Sim branch `detTest`, MMP2_v4) has the wrong mesh pitch and ~5× our
  copper. See `scripts/model/compare_stacks_p2sim.py`.
- **COMSOL mesh cell:** from a Saclay Micromegas colleague (Alexandra can introduce you). The file is
  `/eos/user/a/akallits/p2_sim/comsol/` (850 MB). Use the `h2mm_sweep_gap150` outputs. COMSOL re-meshes on every solve, so you need one solve per voltage.

## 8. Running things

**Without a CERN account, follow `docs/LOCAL_SETUP.md`.** It covers the conda environment,
the data bundle (`$P2_DATA` stands in for `/eos/user/a/akallits/p2_sim`
everywhere in this file), `submit_condor_p2.py --local` in place of HTCondor,
and a check that your machine reproduces the lxplus numbers. The only thing
you cannot do locally is a new COMSOL field solve, which needs a licence.

The rest of this section is for whoever runs on lxplus. `docs/RUNBOOK.md`
covers building and submitting Geant4 jobs. In addition:

- Work from a **clean git clone** so RunMeta records a real commit. Build it with
  `scripts/setup_lxplus.sh` + `scripts/build.sh`.
- Garfield++: pinned commit **927e5c21 + our patch**. Build your own copy in your
  `/afs/cern.ch/work` area; the AFS home area is too small. Source `scripts/setup_garfield.sh`
  (LCG_109 view). Never pipe `source` into `grep` or `tail`, because the environment is lost.
- ROOT 6.38 cling cannot JIT Garfield macros. Write **compiled** programs linked
  with `-lGarfield -lGarfieldRandom` (see `scripts/garfield/run_transparency.sh`).
- `run_transparency.sh` recompiles when the `.cc` is newer than the binary. **Don't edit or
  `git pull` sources while condor jobs that use them are queued.**
- COMSOL 6.4 is on CVMFS with the CERN licence, and there are few seats. Keep
  `MAXJOBS comsol 2` in DAGs. See `scripts/comsol/README.md`.
- HTCondor DAG VARS: a plain assignment in a `.sub` overrides them. Use
  `$(var:default)` and check with `condor_submit -dry-run`.
- Put large outputs on EOS, not AFS. lxplus nodes rotate, so don't use `/tmp`. Run long
  jobs detached (`setsid nohup … &`), because long ssh commands get dropped.
- Kerberos tickets last about a day (`kinit <you>@CERN.CH`). lxplus now asks for a second
  factor.
- Garfield validation results that can be reproduced: `docs/results/mesh/transparency_nikolopoulos.csv`
  (rms 2.4 % against the published data).

## 9. Logbook and slides

- The dated logbook (one slide per step) is a claude.ai page owned by
  Alexandra: https://claude.ai/artifact/TmVumv928tiDApPxyDqSaA. Ask her to share it.
  The source is `docs/logbook/project/` (deck.json + slides/*.html). The live deck has
  layout edits made in the browser that are not in the repo.
- Meeting slides: white background, black text, Arial, title + bullets, at most one figure. Upload to Google Slides
  as a .pptx (`docs/slides/make_rnd_slides.py`).

## 10. Suggested first two weeks

1. Read this file, `CLAUDE.md`, `docs/P2_GEOMETRY.md` and `docs/results/mesh/README.md`.
   Then go through the logbook slides.
2. Install locally and download the data bundle (`docs/LOCAL_SETUP.md` §1–2;
   Alexandra sends the CERNBox link).
3. **Reproduce known results before changing anything**: the checks in
   `docs/LOCAL_SETUP.md` §4. They rerun a published transparency point and one
   `rnd2026_heed` point, and compare them with the lxplus results. This tests your setup and
   these documents. Fix any step that was wrong.
4. Then start on to-do item 1 (geometry vs data).

## 11. People

- **Alexandra Kallitsopoulou** (CEA Saclay): the previous owner of this work. She can answer questions about
  geometry, run conditions, design decisions and history.
- **Matthieu Gailliard**: P2Sim, background spectra, beam current.
- **Dylan** (CERN user `dneff`): MX17 detectors. He uses this model. The exchange about PIXE and Heed is in
  `docs/results/heed/pai/REPLY_to_Dylan_2026-10-16.md`. He also owns the SPS run_config files on EOS.
- Saclay Micromegas colleague: the COMSOL woven-mesh model.
- The data-analysis side (gap/timing, cosmic): `../P2_basket_analysis/`.
