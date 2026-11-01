# build_prog.sh — sourced by run_transparency.sh, run_gain.sh, run_heed.sh.
#
#   p2_garfield_env            # sets up Garfield++ (lxplus or local), sets $here
#   p2_build_prog <name>       # compiles scripts/garfield/<name>.cc if needed,
#                              # sets $exe
#
# Garfield install, in order: $P2_GARFIELD_INSTALL, the lxplus work-area
# install (if it exists), ~/garfield/install (what
# `bash scripts/setup_garfield.sh --build` produces on any machine).

p2_garfield_env() {
    here="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
    # Under HTCondor the script is copied to the job scratch: use the clone.
    [ -f "$here/scripts/setup_garfield.sh" ] || here="${P2_REPO:-$HOME/P2_Geant_Garfield}"
    if [ -z "$P2_GARFIELD_INSTALL" ]; then
        for _c in /afs/cern.ch/work/a/akallits/garfield/install "$HOME/garfield/install"; do
            if [ -d "$_c/include/Garfield" ]; then P2_GARFIELD_INSTALL="$_c"; break; fi
        done
    fi
    export P2_GARFIELD_INSTALL
    source "$here/scripts/setup_garfield.sh"
    if [ -z "$GARFIELD_INSTALL" ] || [ ! -d "$GARFIELD_INSTALL/include/Garfield" ]; then
        echo "No Garfield++ install found. Build it: bash scripts/setup_garfield.sh --build" >&2
        exit 1
    fi
    _glib="$GARFIELD_INSTALL/lib64"
    [ -d "$_glib" ] || _glib="$GARFIELD_INSTALL/lib"
}

p2_build_prog() {
    local src="$here/scripts/garfield/$1.cc"
    exe="$GARFIELD_INSTALL/../bin/$1"
    if [ ! -x "$exe" ] || [ "$src" -nt "$exe" ]; then
        mkdir -p "$(dirname "$exe")"
        # build to a private name and rename: parallel jobs must not race
        "${CXX:-g++}" -O2 -std=c++20 -o "$exe.$(hostname).$$" "$src" \
            -I"$GARFIELD_INSTALL/include" $(root-config --cflags --libs) \
            -L"$_glib" -lGarfield -lGarfieldRandom -Wl,-rpath,"$_glib"
        mv -f "$exe.$(hostname).$$" "$exe"
    fi
}
