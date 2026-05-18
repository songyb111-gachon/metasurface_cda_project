"""
Tidy3D FDTD vs CDA cross-validation.

We build a 2D-equivalent FDTD simulation of a 1D array of Lorentz-
medium cylinders.  Plane-wave illumination is TM (E along the cylinder
axis z), which matches the scalar Helmholtz problem CDA solves.

Usage:
    python run_fdtd_comparison.py --estimate
    python run_fdtd_comparison.py --confirm --periods 0.6 0.8 1.0 1.2 1.5 --N 11

API key is read from a local `.env` (TIDY3D_APIKEY=...) or environment.
"""

from __future__ import annotations

import argparse
import os
import json
import sys

import numpy as np
import matplotlib.pyplot as plt

import cda
from run_baseline import (
    DEFAULT_OMEGA,
    DEFAULT_OMEGA0,
    DEFAULT_GAMMA,
    DEFAULT_F,
    FIG_DIR,
)

# Force UTF-8 console (Tidy3D log messages contain Greek letters etc.)
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(HERE, "fdtd_results")
os.makedirs(RESULTS_DIR, exist_ok=True)


# ---------------------------------------------------------------------
# API key loading (env var or .env)
# ---------------------------------------------------------------------
def load_api_key() -> str | None:
    key = os.environ.get("TIDY3D_APIKEY")
    if key:
        return key
    env_path = os.path.join(HERE, ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("#") or not line:
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    if k.strip() == "TIDY3D_APIKEY":
                        return v.strip().strip('"').strip("'")
    return None


# ---------------------------------------------------------------------
# Conventions
# ---------------------------------------------------------------------
LAMBDA0 = 1.0                          # 1 um  (Tidy3D length unit)
C_LIGHT = 299792458.0e6                # speed of light in um/s
FREQ0 = C_LIGHT / LAMBDA0              # ~300 THz
FWIDTH = 0.05 * FREQ0
RUN_TIME = 5e-13                       # 500 fs


def make_lorentz_medium():
    """Single-pole Lorentz medium with modest Δε to avoid in-medium grid blow-up."""
    import tidy3d as td
    f_res = 1.05 * FREQ0
    delta = 0.4 * FREQ0
    return td.Lorentz(eps_inf=2.0, coeffs=[(1.5, f_res, delta)])


def make_simulation(period_lambda: float, N: int = 11,
                    cylinder_radius_lambda: float = 0.08):
    """2D-equivalent simulation: PML in x and y, periodic in z.
    Returns (sim, atom_x, monitor_name).
    """
    import tidy3d as td

    period = period_lambda * LAMBDA0
    radius = cylinder_radius_lambda * LAMBDA0

    array_span = (N - 1) * period
    pad_x = 2.0 * LAMBDA0
    pad_y_below = 3.0 * LAMBDA0
    pad_y_above = 3.0 * LAMBDA0
    sx = array_span + 2 * pad_x
    sy = pad_y_below + pad_y_above
    sz = LAMBDA0 * 0.2

    medium = make_lorentz_medium()

    atom_x = np.arange(N) * period
    atom_x -= atom_x.mean()

    y_center = (-pad_y_below + pad_y_above) / 2.0
    y_min = -pad_y_below
    src_y = y_min + 1.2 * LAMBDA0     # safely outside PML

    src = td.PlaneWave(
        source_time=td.GaussianPulse(freq0=FREQ0, fwidth=FWIDTH),
        center=(0, src_y, 0),
        size=(td.inf, 0, td.inf),
        direction="+",
        pol_angle=np.pi / 2.0,         # E along z (cylinder axis) -> TM scalar
    )

    mon_field = td.FieldMonitor(
        center=(0, y_center, 0),
        size=(max(array_span + 0.6 * LAMBDA0, 1.0 * LAMBDA0), 0, 0),
        freqs=[FREQ0],
        name="atoms_line",
    )
    mon_trans = td.FluxMonitor(
        center=(0, y_center + 1.0 * LAMBDA0, 0),
        size=(td.inf, 0, td.inf),
        freqs=[FREQ0],
        name="trans",
    )

    cylinders = []
    for x in atom_x:
        cylinders.append(td.Structure(
            geometry=td.Cylinder(center=(x, y_center, 0.0),
                                 radius=radius, length=td.inf, axis=2),
            medium=medium,
        ))

    sim = td.Simulation(
        size=(sx, sy, sz), center=(0, 0, 0),
        grid_spec=td.GridSpec.uniform(dl=LAMBDA0 / 15.0),
        structures=cylinders,
        sources=[src],
        monitors=[mon_field, mon_trans],
        run_time=RUN_TIME,
        boundary_spec=td.BoundarySpec(
            x=td.Boundary.pml(),
            y=td.Boundary.pml(),
            z=td.Boundary.periodic(),
        ),
        medium=td.Medium(permittivity=1.0),
    )
    return sim, atom_x, "atoms_line"


# ---------------------------------------------------------------------
# Cost estimation
# ---------------------------------------------------------------------
def estimate_cost(period_lambdas):
    print("=" * 70)
    print("Cost estimate (no simulations submitted)")
    print("=" * 70)
    total = 0
    for P in period_lambdas:
        sim, _, _ = make_simulation(P)
        n_cells = int(np.prod(sim.num_cells))
        total += n_cells
        print(f"  P = {P:>4.2f} λ    grid cells = {n_cells:>12,d}")
    print(f"  Total grid cells over {len(period_lambdas)} sims: {total:,d}")
    print("  (Use the Tidy3D web UI to see exact FlexCredit cost.)")


# ---------------------------------------------------------------------
# Solver execution
# ---------------------------------------------------------------------
def run_one(sim, atom_x, monitor_name):
    """Submit sim, return per-atom complex E_z at the array line."""
    from tidy3d import web
    task_id = web.upload(sim, task_name=f"cda_validation_{np.random.randint(1e6)}")
    web.start(task_id)
    web.monitor(task_id)
    sim_data = web.load(task_id)
    fld = sim_data[monitor_name]
    Ez = fld.Ez
    return np.array([
        complex(Ez.sel(x=x, method="nearest").values.flatten()[0])
        for x in atom_x
    ]), sim_data


def run_pipeline(period_lambdas, N=11, dry_run=True):
    fdtd_phases = {}
    fdtd_amps = {}
    isolated_phase = None

    if not dry_run:
        print("Step 1: single-particle calibration ...")
        sim_cal, atom_x_cal, mon = make_simulation(period_lambda=20.0, N=1)
        Ez_cal, _ = run_one(sim_cal, atom_x_cal, mon)
        isolated_phase = float(np.angle(Ez_cal[0]))
        print(f"  isolated phase reference = {np.degrees(isolated_phase):.3f} deg")

        for P in period_lambdas:
            print(f"Step 2: array sweep at P = {P} lambda ...")
            sim, atom_x, mon = make_simulation(period_lambda=P, N=N)
            Ez, _ = run_one(sim, atom_x, mon)
            fdtd_phases[P] = np.angle(Ez)
            fdtd_amps[P] = np.abs(Ez)
            print(f"  |Ez| range = [{fdtd_amps[P].min():.3e}, {fdtd_amps[P].max():.3e}]")

        out = {
            "period_lambdas": list(map(float, period_lambdas)),
            "isolated_phase_rad": isolated_phase,
            "phases": {f"{P:.3f}": fdtd_phases[P].tolist() for P in period_lambdas},
            "amps":   {f"{P:.3f}": fdtd_amps[P].tolist()   for P in period_lambdas},
        }
        out_path = os.path.join(RESULTS_DIR, "fdtd_data.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2)
        print(f"FDTD raw data saved: {out_path}")
        return out
    else:
        print("DRY RUN — no simulations submitted.")
        return None


# ---------------------------------------------------------------------
# CDA-side prediction
# ---------------------------------------------------------------------
def cda_phase_at_periods(period_lambdas, N=11):
    alpha = cda.LorentzAlpha(
        omega0=DEFAULT_OMEGA0, gamma=DEFAULT_GAMMA, F=DEFAULT_F
    )(omega=DEFAULT_OMEGA)
    out = {}
    for P in period_lambdas:
        res = cda.run_uniform_array(N=N, period=P, alpha=alpha)
        out[P] = cda.phase_deviation(res["p_coupled"], res["p_isolated"])
    return out


# ---------------------------------------------------------------------
# Plot — both on the same axes
# ---------------------------------------------------------------------
def plot_comparison(period_lambdas, fdtd_data, N=11):
    cda_phases = cda_phase_at_periods(period_lambdas, N=N)
    P_arr = np.array(period_lambdas)
    cda_means = np.array([
        np.degrees(np.mean(np.abs(cda_phases[P]))) for P in period_lambdas
    ])
    cda_max = np.array([
        np.degrees(np.max(np.abs(cda_phases[P]))) for P in period_lambdas
    ])

    fdtd_means = None
    fdtd_max = None
    if fdtd_data is not None:
        fdtd_means = []
        fdtd_max = []
        ref = fdtd_data["isolated_phase_rad"]
        for P in period_lambdas:
            ph = np.array(fdtd_data["phases"][f"{P:.3f}"])
            dev = np.angle(np.exp(1j * (ph - ref)))
            fdtd_means.append(np.degrees(np.mean(np.abs(dev))))
            fdtd_max.append(np.degrees(np.max(np.abs(dev))))
        fdtd_means = np.array(fdtd_means)
        fdtd_max = np.array(fdtd_max)

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.plot(P_arr, cda_means, "o-", color="#1A478A", lw=2.2,
            markersize=8, label="CDA — mean")
    ax.plot(P_arr, cda_max, "o--", color="#1A478A", lw=1.0,
            markersize=6, alpha=0.5, label="CDA — max")
    if fdtd_means is not None:
        ax.plot(P_arr, fdtd_means, "s-", color="#C0392B", lw=2.2,
                markersize=8, label="FDTD — mean")
        ax.plot(P_arr, fdtd_max, "s--", color="#C0392B", lw=1.0,
                markersize=6, alpha=0.5, label="FDTD — max")
    for m in [1.0]:
        ax.axvline(m, color="gray", linestyle=":", alpha=0.7)
        ax.text(m, ax.get_ylim()[1] * 0.95, "  P = λ\n  (Wood anomaly)",
                fontsize=9, color="gray", verticalalignment="top")
    if fdtd_means is None:
        ax.text(0.05, 0.92,
                "FDTD data not available (run with --confirm)",
                transform=ax.transAxes, fontsize=11,
                color="#C0392B", verticalalignment="top",
                bbox=dict(facecolor="#FFEFEF", edgecolor="#C0392B"))
    ax.set_xlabel(r"period  $P$  (units of $\lambda$)")
    ax.set_ylabel(r"$|\Delta\varphi|$  (deg)")
    ax.set_title(
        f"Coupling-induced phase deviation: CDA vs Tidy3D FDTD  (N = {N})\n"
        "Both: TM polarization (E along cylinder axis)"
    )
    ax.grid(alpha=0.3)
    ax.legend(loc="upper right", ncol=2)
    fig.tight_layout()
    out = os.path.join(FIG_DIR, "fdtd_vs_cda_comparison.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"comparison figure saved: {out}")
    return out


# ---------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--estimate", action="store_true")
    parser.add_argument("--confirm", action="store_true")
    parser.add_argument("--periods", type=float, nargs="+",
                        default=[0.6, 0.8, 1.0, 1.2, 1.5])
    parser.add_argument("--N", type=int, default=11)
    args = parser.parse_args()

    print("=" * 70)
    print("FDTD (Tidy3D) vs CDA  --  validation script")
    print("=" * 70)
    print(f"  periods = {args.periods}")
    print(f"  N = {args.N}\n")

    api_key = load_api_key()
    if api_key:
        try:
            import tidy3d as td
            from tidy3d import web
            web.configure(api_key)
            print("[OK]  tidy3d configured")
        except Exception as e:
            print(f"[WARN] tidy3d configure failed: {e}")
    else:
        print("[WARN] No TIDY3D_APIKEY found; only --estimate possible.")

    if args.estimate:
        try:
            estimate_cost(args.periods)
        except Exception as e:
            print(f"[ERROR] cost estimation failed: {e}")
        plot_comparison(args.periods, fdtd_data=None, N=args.N)
        return

    fdtd_data = None
    if args.confirm:
        if not api_key:
            print("[ERROR] --confirm requires API key")
            sys.exit(2)
        fdtd_data = run_pipeline(args.periods, N=args.N, dry_run=False)
    else:
        cached = os.path.join(RESULTS_DIR, "fdtd_data.json")
        if os.path.exists(cached):
            with open(cached, "r", encoding="utf-8") as f:
                fdtd_data = json.load(f)
            print(f"[OK]  loaded cached FDTD data: {cached}")

    plot_comparison(args.periods, fdtd_data, N=args.N)


if __name__ == "__main__":
    main()
