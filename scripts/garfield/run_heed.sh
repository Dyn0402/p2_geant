#!/usr/bin/env bash
# run_heed.sh <gas> <gap_mm> <theta_deg> <n> <out> [particle] [E_kin_eV] [seed]
# Builds (if needed) and runs scripts/garfield/heed_mip.cc with the pinned
# Garfield build (see build_prog.sh).
set -e
# Under HTCondor this script is copied to the job scratch: fall back to the clone.
_bp="$(dirname "$0")/build_prog.sh"
[ -f "$_bp" ] || _bp="${P2_REPO:-$HOME/P2_Geant_Garfield}/scripts/garfield/build_prog.sh"
source "$_bp"
p2_garfield_env
mkdir -p "$(dirname "$5")"
p2_build_prog heed_mip
"$exe" "$@"
