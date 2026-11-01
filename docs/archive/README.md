# Archive: August 2026 planning docs

You don't need these to start. They are the planning and handoff documents from
August 2026, when the repo was set up on lxplus. Most of their status sections
are out of date. Anything still relevant has been copied into `../HANDOVER.md`,
`../OPEN_PROBLEMS.md` or `../SETUP.md`.

Code comments that cite **"plan §N"** or a task number **P0.x** mean
`SIM_CAMPAIGN_PLAN.md` here.

| file | what it was | still worth reading for |
|---|---|---|
| `SIM_CAMPAIGN_PLAN.md` | the August campaign plan (phases, run matrices, chain design) | §1 physics framing, §2 chain architecture, **§7 gas candidates** (Ne mixtures, flammability, procurement) |
| `TESTBEAM_PLAN.md`, `testbeam/` | plan and fill-in template for the SPS comparison | §4 observable ↔ parameter matrix, §6 "don't tune past these" |
| `NEEDED_INPUTS.md` | register of guessed inputs | §1–2 (signal-electron phase space), §5–6 (VMM noise, Ne gain); summarised in `../OPEN_PROBLEMS.md` |
| `HANDOFF_MX17_RESPONSE.md` | exchange with the MX17 simulation | §2.6, a measured warning for any future weighting-field solve |
| `RUNBOOK.md` | lxplus how-to | pitfalls moved to `../SETUP.md` §5 |
| `BENCHMARKS.md`, `benchmark_lxplus.sh` | first speed measurements (lxplus) | cost model: ~2000 γ/s, ~550 e⁻/s per core, ~6.5 s startup per job |
| `SIM_CAMPAIGN_BRIEF.md`, `HANDOFF.md` | first-day snapshots | history only |
| `MX17_README.md` | README of the MX17 code this repo grew from | the non-P2 modes (`-m vacuum/full/sr90`) |
| `campaign_plan_html/` | HTML/PDF renderings of the campaign plan | history only |
