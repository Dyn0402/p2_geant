# Legacy: MX17 scripts

This repo started as a copy of the MX17 (n-TOF X17) Micromegas simulation. Its
non-P2 geometry modes (`-m vacuum`, `full`, `sr90`, `lscalib`) are still in
`src/`. The submission and analysis scripts for those modes are kept here.
**None of them are used for P2**, where the entry point is
`scripts/submit_condor_p2.py`. Documentation: `docs/archive/MX17_README.md`.
