# P2 Micromegas simulation

Simulation of the P2 (MESA, Mainz) wedge Micromegas, from the particle to the
VMM3a readout:

```
Geant4 (mm_sim)  ->  Garfield++ / Magboltz  ->  Stage B (stage_b/)  ->  VMM emulator (vmm/)
ionization in        mesh transparency,         per-pad charge           threshold, timing,
the drift gas        gain (COMSOL field maps)   and time                 efficiency
```

The current question is how to raise the gas gain to make up for the VMM
threshold loss seen at the SPS (VMM 85 % vs DREAM 96 % efficiency) while
keeping ≲ 20 ns timing.

## Start here

1. [`docs/HANDOVER.md`](docs/HANDOVER.md): what the project is, where it stands, your first task.
2. [`docs/SETUP.md`](docs/SETUP.md): install and run, on Feynman (CEA cluster) or your laptop. No CERN account needed.
3. [`CLAUDE.md`](CLAUDE.md): the working rules. Read them before you produce a number.
4. [`docs/HOWTO.md`](docs/HOWTO.md): recipes for everyday tasks (run a scan, a Garfield sweep, a gas table, compare with data, troubleshooting).

## Where things are

| | |
|---|---|
| `mm_sim.cc`, `src/`, `include/` | Geant4 application (`-m p2` is the default mode) |
| `scripts/garfield/`, `scripts/comsol/` | mesh transparency and gain (Garfield++), field maps (COMSOL) |
| `stage_b/`, `vmm/` | drift/avalanche/induction to pads; VMM3a emulator |
| `scripts/analysis/` | analyses behind `docs/results/` |
| `scripts/submit_condor_p2.py` | runs a scan: `--slurm` (Feynman), `--local N` (laptop), or HTCondor (lxplus) |
| `docs/results/` | results with the script that made each one |
| `docs/OPEN_PROBLEMS.md` | open physics questions and the to-do list |
| `docs/P2_GEOMETRY.md`, `docs/P2_MODEL.md` | every geometry number and its source; what the simulation builds |
| `docs/OUTPUT_FORMAT.md` | ROOT output (RunMeta, EventTree, ClusterTree) |
| `docs/research/`, `docs/P2_EXPERIMENT.md` | background notes with sources |
| `docs/logbook/` | source of the dated logbook slides |
| `design/` | fabrication files (gerbers, masks, drawings) |
| `docs/archive/`, `legacy/` | August planning docs and MX17 scripts; not needed to start |
