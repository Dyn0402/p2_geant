#!/usr/bin/env bash
# make_data_bundle.sh — pack the EOS/AFS data a non-CERN user needs into
# tarballs, for sharing through a CERNBox public link.
#
# Run ON LXPLUS by someone with read access to /eos/user/a/akallits/p2_sim:
#
#   bash scripts/make_data_bundle.sh --dry-run      # list what goes in, sizes
#   bash scripts/make_data_bundle.sh                # core bundle (~9 GB)
#   bash scripts/make_data_bundle.sh --with-optional
#
# Output: $OUT (default /eos/user/a/akallits/p2_sim/handover_bundle), one
# .tar per item plus SHA256SUMS and MANIFEST.txt. Share that folder in CERNBox
# ("Share" -> "Public link", read-only). Recipients extract every tarball into
# $P2_DATA (docs/SETUP.md); paths inside are relative to p2_sim/, so
# /eos/user/a/akallits/p2_sim/X becomes $P2_DATA/X.
set -euo pipefail

SRC="${SRC:-/eos/user/a/akallits/p2_sim}"
AFS_CLONE="${AFS_CLONE:-$HOME/P2_Geant_Garfield}"
OUT="${OUT:-/eos/user/a/akallits/p2_sim/handover_bundle}"

# name | path relative to $SRC | why
CORE=(
  "gas_tables|gas_tables|Magboltz .gas tables, 6 dry mixtures (Garfield, Stage B)"
  "gas_tables_contam|gas_tables_contam|Ar/CO2/iso + O2/H2O tables (contamination fit)"
  "rnd2026_heed|rnd2026_heed|production Geant4 batch, Heed physics (cluster 12558227)"
  "cell_gap150|comsol/p2_sps/h2mm_sweep_gap150|COMSOL field maps of the final cell, 8 drift fields"
  "transparency|transparency|Garfield transparency outputs (all studies)"
)
OPTIONAL=(
  "cell_nik|comsol/p2_sps/h2mm_sweep_nik|Nikolopoulos validation cell (reproduce the 2.4 % rms check)"
  "cell_gaps_gap150|comsol/p2_sps/gaps_gap150|drift-gap scan cells 4-8 mm"
  "cell_vm415|comsol/p2_sps/h2mm_sweep_vm415|cosmic-bench cell (mesh 415 V)"
  "rnd2026_mylar50|rnd2026_mylar50|legacy-physics batch (comparison only; do not use nPrimDrift)"
  "comsol_model|comsol/MeshUnitCellIon_PressureStudy.mph|COMSOL 6.3 model (needs a COMSOL licence)"
)
# The geometry-DAG cells (h2mm_sweep_g120/g135/g165/p66/p73/rw8/rw10, *_vm430/470,
# ~60 GB) are only needed to rerun Garfield on them; their results are in
# condor_transp below.

dry=0; items=("${CORE[@]}")
for a in "$@"; do
  case "$a" in
    --dry-run) dry=1 ;;
    --with-optional) items+=("${OPTIONAL[@]}") ;;
    *) echo "unknown option $a" >&2; exit 2 ;;
  esac
done

[ $dry = 1 ] || mkdir -p "$OUT"
manifest="$OUT/MANIFEST.txt"
[ $dry = 1 ] || : > "$manifest"

for it in "${items[@]}"; do
  IFS='|' read -r name rel why <<< "$it"
  size=$(du -sh "$SRC/$rel" | cut -f1)
  printf '%-18s %6s  %s\n' "$name" "$size" "$why"
  [ $dry = 1 ] && continue
  if [ -f "$OUT/$name.tar" ]; then echo "  (exists, skipped)"; continue; fi
  tar -C "$SRC" -cf "$OUT/$name.tar.part" "$rel"
  mv "$OUT/$name.tar.part" "$OUT/$name.tar"
  printf '%-18s %6s  %-45s %s\n' "$name.tar" "$size" "$rel" "$why" >> "$manifest"
done

# Garfield job logs of the geometry DAG (TRANSPARENCY / GAIN lines): on AFS,
# not EOS. Packed as condor_transp/ under $P2_DATA.
size=$(du -sh "$AFS_CLONE/condor_transp" | cut -f1)
printf '%-18s %6s  %s\n' condor_transp "$size" "geometry-DAG + gap-scan Garfield logs (AFS)"
if [ $dry = 0 ]; then
  tar -C "$AFS_CLONE" -cf "$OUT/condor_transp.tar" condor_transp
  printf '%-18s %6s  %-45s %s\n' condor_transp.tar "$size" "condor_transp" \
    "geometry-DAG + gap-scan Garfield logs" >> "$manifest"
  (cd "$OUT" && sha256sum *.tar > SHA256SUMS)
  echo; echo "Done: $OUT  — share it in CERNBox as a read-only public link."
fi
