#!/usr/bin/env bash
# run_gain.sh <cell> <gasfile> <out> <r1,r2,...> [n]
#
# Builds (if needed) and runs scripts/garfield/mesh_gain.cc with the pinned
# Garfield build (see build_prog.sh).
#
#   bash scripts/garfield/run_gain.sh \
#     $P2_DATA/comsol/p2_sps/h2mm_sweep_gap150/E625 \
#     $P2_DATA/gas_tables/ArCO2Iso9352.gas \
#     $P2_DATA/gain/test 0,0.2,0.4 10
#   (on lxplus P2_DATA = /eos/user/a/akallits/p2_sim)
set -e
# Under HTCondor this script is copied to the job scratch: fall back to the clone.
_bp="$(dirname "$0")/build_prog.sh"
[ -f "$_bp" ] || _bp="${P2_REPO:-$HOME/P2_Geant_Garfield}/scripts/garfield/build_prog.sh"
source "$_bp"
p2_garfield_env
mkdir -p "$(dirname "$3")"
p2_build_prog mesh_gain
"$exe" "$1" "$2" "$3" "$4" "${5:-20}"
