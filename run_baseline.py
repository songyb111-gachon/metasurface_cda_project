"""
Baseline run for the CDA project.

  1. Single-dipole sanity check (CDA == α · E_inc to machine precision)
  2. Baseline figure: phase deviation across a uniform 1D array
  3. Limiting-case figure: mean phase deviation vs period
"""

from __future__ import annotations

import os
import numpy as np
import matplotlib.pyplot as plt

import cda

HERE = os.path.dirname(os.path.abspath(__file__))
FIG_DIR = os.path.join(HERE, "figures")
os.makedirs(FIG_DIR, exist_ok=True)


# Reference operating point used across the whole project.
DEFAULT_OMEGA  = 2.0 * np.pi          # operating frequency (λ = 1)
DEFAULT_OMEGA0 = 2.1 * np.pi          # detuned Lorentz resonance
DEFAULT_GAMMA  = 0.4
DEFAULT_F      = 4.0


def default_alpha() -> complex:
    return cda.LorentzAlpha(
        omega0=DEFAULT_OMEGA0, gamma=DEFAULT_GAMMA, F=DEFAULT_F
    )(omega=DEFAULT_OMEGA)


def sanity_check_single_dipole() -> dict:
    alpha = default_alpha()
    res = cda.run_uniform_array(N=1, period=1.0, alpha=alpha)
    p_num, p_ana = res["p_coupled"][0], alpha * 1.0
    err_abs = abs(p_num - p_ana)
    err_rel = err_abs / abs(p_ana)
    print("=" * 60)
    print("Sanity check: single isolated dipole")
    print("=" * 60)
    print(f"  alpha                = {alpha:.6e}")
    print(f"  p (CDA numerical)    = {p_num:.6e}")
    print(f"  p (analytical α·E)   = {p_ana:.6e}")
    print(f"  |error|              = {err_abs:.3e}")
    print(f"  relative error       = {err_rel:.3e}")
    print()
    return {"alpha": alpha, "p_num": p_num, "p_ana": p_ana,
            "err_abs": err_abs, "err_rel": err_rel}


def baseline_figure(N: int = 31, period: float = 0.6) -> dict:
    alpha = default_alpha()
    res = cda.run_uniform_array(N=N, period=period, alpha=alpha)
    positions = res["positions"]
    phase_dev = np.degrees(res["phase_dev"])
    adr = cda.amplitude_distortion_ratio(res["p_coupled"], res["p_isolated"])
    mean_dev = np.degrees(res["mean_phase_dev"])
    max_dev  = np.degrees(res["max_phase_dev"])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.2))

    ax1.plot(positions, phase_dev, "o-", color="#C0392B")
    ax1.axhline(0, color="k", lw=0.5)
    ax1.set_xlabel(r"atom position $x$  (units of $\lambda$)")
    ax1.set_ylabel(r"phase deviation $\Delta\varphi$  (deg)")
    ax1.set_title(
        f"Uniform array  N = {N}, P = {period:.2f}λ\n"
        f"mean |Δφ| = {mean_dev:.2f}°,  max |Δφ| = {max_dev:.2f}°"
    )
    ax1.grid(alpha=0.3)

    ax2.plot(positions, adr, "s-", color="#1A478A")
    ax2.axhline(1, color="k", lw=0.5)
    ax2.set_xlabel(r"atom position $x$  (units of $\lambda$)")
    ax2.set_ylabel(r"amplitude ratio $|p_{coup}|/|p_{iso}|$")
    ax2.set_title("Amplitude distortion ratio")
    ax2.grid(alpha=0.3)

    fig.tight_layout()
    out = os.path.join(FIG_DIR, "baseline_uniform_array.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)

    print("=" * 60)
    print(f"Baseline figure  N = {N}, P = {period} λ")
    print("=" * 60)
    print(f"  mean |Δφ|  = {mean_dev:7.3f} deg")
    print(f"  max  |Δφ|  = {max_dev:7.3f} deg")
    print(f"  ADR range  = [{adr.min():.4f}, {adr.max():.4f}]")
    print(f"  figure     : {out}")
    print()
    return {"mean_dev": mean_dev, "max_dev": max_dev,
            "adr_min": float(adr.min()), "adr_max": float(adr.max()),
            "figure": out}


def limiting_case_figure(N: int = 21) -> dict:
    alpha = default_alpha()
    periods = np.linspace(0.5, 10.0, 40)
    devs = []
    for P in periods:
        res = cda.run_uniform_array(N=N, period=P, alpha=alpha)
        devs.append(np.degrees(res["mean_phase_dev"]))
    devs = np.array(devs)

    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    ax.plot(periods, devs, "o-", color="#1A478A", markersize=4)
    ax.axhline(0, color="k", lw=0.5)
    ax.set_xlabel(r"period $P$  (units of $\lambda$)")
    ax.set_ylabel(r"mean $|\Delta\varphi|$  (deg)")
    ax.set_title(f"Mean phase deviation vs period  (N = {N})")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    out = os.path.join(FIG_DIR, "limiting_case_period.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)

    print("=" * 60)
    print(f"Limiting-case figure  : {out}")
    print(f"  Δφ at P = 0.5 λ  : {devs[0]:7.3f} deg")
    print(f"  Δφ at P = 10  λ  : {devs[-1]:7.3f} deg")
    print()
    return {"periods": periods.tolist(), "mean_dev": devs.tolist(),
            "figure": out}


if __name__ == "__main__":
    sanity_check_single_dipole()
    baseline_figure(N=31, period=0.6)
    limiting_case_figure(N=21)
    print("Baseline complete. See ./figures/.")
