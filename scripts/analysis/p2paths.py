"""p2paths.py — where the analysis scripts find their input data.

Order: an explicit environment variable, then the data bundle under $P2_DATA
(docs/SETUP.md §3), then the original location on Alexandra's laptop.

    P2_SPS_PRODUCTS    SPS products: <det>/<scan>/.../beam_mpv_vs_hv_spark_vetoed.csv
                       default $P2_DATA/sps_products/analysis
    P2_COSMIC_PRODUCTS cosmic-bench products (Fe55):  default $P2_DATA/cosmic_products
    P2_BASKET_ANALYSIS checkout of the P2_basket_analysis repo (cosmic_bench_analysis code)
"""
import os
from pathlib import Path

P2_DATA = Path(os.environ.get("P2_DATA", Path.home() / "p2_data"))
_LAPTOP = Path("/local/home/ak271430/Documents/PostDocSaclay")


def _first(env, *candidates):
    if os.environ.get(env):
        return Path(os.environ[env])
    for c in candidates:
        if c.exists():
            return c
    raise FileNotFoundError(
        f"{env} not set and none of {', '.join(map(str, candidates))} exists. "
        f"Extract sps_products.tar into $P2_DATA (docs/SETUP.md §3) or set {env}.")


def sps_products():
    return _first("P2_SPS_PRODUCTS", P2_DATA / "sps_products" / "analysis",
                  _LAPTOP / "data/SPS_Beam_Test/mpgd26_workspace/products/analysis")


def sps_run_configs():
    return _first("P2_SPS_RUNS", P2_DATA / "sps_products" / "runs",
                  _LAPTOP / "data/SPS_Beam_Test/mpgd26_workspace/eos_inventory/runs")


def cosmic_products():
    return _first("P2_COSMIC_PRODUCTS", P2_DATA / "cosmic_products",
                  _LAPTOP / "data/Cosmic_Bench/Analysis")


def basket_analysis():
    return _first("P2_BASKET_ANALYSIS", Path.home() / "P2_basket_analysis",
                  _LAPTOP / "P2_basket_analysis")
