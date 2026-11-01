#!/usr/bin/env bash
# run_transparency.sh <mode> <cell> <gasfile|""> <out> [n] [seed] [flags]
#
# Builds (if needed) and runs scripts/garfield/mesh_transparency.cc with the
# pinned Garfield build (see build_prog.sh for where it is looked for).
#
#   lxplus: bash scripts/garfield/run_transparency.sh transp \
#             /eos/user/a/akallits/p2_sim/comsol/p2_sps/h4mm \
#             /eos/user/a/akallits/p2_sim/gas_tables/ArIso.gas \
#             /eos/user/a/akallits/p2_sim/transparency/h4mm_ArIso 2000
#   local : the same with $P2_DATA in place of /eos/user/a/akallits/p2_sim
set -e
# Under HTCondor this script is copied to the job scratch: fall back to the clone.
_bp="$(dirname "$0")/build_prog.sh"
[ -f "$_bp" ] || _bp="${P2_REPO:-$HOME/P2_Geant_Garfield}/scripts/garfield/build_prog.sh"
source "$_bp"
p2_garfield_env
mkdir -p "$(dirname "$4")"
p2_build_prog mesh_transparency
"$exe" "$1" "$2" "$3" "$4" "${5:-2000}" "${6:-1}" "${7:-}"
