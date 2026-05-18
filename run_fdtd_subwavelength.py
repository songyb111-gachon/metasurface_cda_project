"""
Add 5 extra FDTD points in the sub-wavelength window so the CDA
power-law fit can be cross-checked by an independent FDTD fit on the
same range.  Augments the cache `fdtd_results/fdtd_data.json` in place.
"""

from __future__ import annotations

import os
import sys
import json
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_fdtd_comparison import (
    RESULTS_DIR,
    load_api_key,
    make_simulation,
    run_one,
)

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

EXTRA_PERIODS = [0.55, 0.65, 0.70, 0.75, 0.85]
N = 11
DATA_PATH = os.path.join(RESULTS_DIR, "fdtd_data.json")


def main():
    api_key = load_api_key()
    if not api_key:
        print("[ERROR] no TIDY3D_APIKEY found")
        sys.exit(2)
    import tidy3d as td
    from tidy3d import web
    web.configure(api_key)
    print("[OK] tidy3d configured")

    if not os.path.exists(DATA_PATH):
        print(f"[ERROR] {DATA_PATH} not found. Run run_fdtd_comparison.py --confirm first.")
        sys.exit(2)

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"existing periods: {data['period_lambdas']}")

    new_periods = []
    for P in EXTRA_PERIODS:
        key = f"{P:.3f}"
        if key in data["phases"]:
            print(f"  P = {P} already in cache. Skipping.")
            continue
        print(f"submitting FDTD at P = {P} λ ...")
        sim, atom_x, mon = make_simulation(period_lambda=P, N=N)
        Ez, _ = run_one(sim, atom_x, mon)
        data["phases"][key] = np.angle(Ez).tolist()
        data["amps"][key]   = np.abs(Ez).tolist()
        new_periods.append(float(P))
        print(f"  |Ez| range = [{min(data['amps'][key]):.3e}, {max(data['amps'][key]):.3e}]")

    all_P = sorted(set(data["period_lambdas"]) | set(new_periods))
    data["period_lambdas"] = list(map(float, all_P))
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"updated cache: {DATA_PATH}")
    print(f"final periods: {data['period_lambdas']}")


if __name__ == "__main__":
    main()
