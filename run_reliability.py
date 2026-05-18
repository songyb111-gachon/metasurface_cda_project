"""
Reliability / robustness analyses for the final report.

  R1. Random α-profiles reliability across multiple seeds + grading widths
      → median + 5/95 percentile band of the increase law β
  R2. Grading magnitude sensitivity   — small vs large ω₀ spread,
      both in terms of (i) mean |Δφ|(P) curve and (ii) fitted β
  R3. N-convergence quantitative      — bulk Δφ̄ extrapolation as N → ∞
"""

from __future__ import annotations

import os
import json
import numpy as np
import matplotlib.pyplot as plt

import cda
from run_baseline import (
    DEFAULT_OMEGA,
    DEFAULT_OMEGA0,
    DEFAULT_GAMMA,
    DEFAULT_F,
    default_alpha,
    FIG_DIR,
)

HERE = os.path.dirname(os.path.abspath(__file__))
SUMMARY_PATH = os.path.join(HERE, "reliability_summary.json")

P_MIN, P_MAX = 0.55, 0.85
PERIODS = np.linspace(P_MIN, P_MAX, 31)


def _mean_dev_uniform(N, period, alpha=None):
    if alpha is None:
        alpha = default_alpha()
    return float(np.degrees(cda.run_uniform_array(N=N, period=period, alpha=alpha)["mean_phase_dev"]))


def _mean_dev_nonuniform(N, period, alphas):
    pos = cda.linear_array(N, period)
    return float(np.degrees(cda.run_nonuniform_array(positions=pos, alphas=alphas)["mean_phase_dev"]))


def _fit_beta(P, dev):
    pos = dev > 0
    if pos.sum() < 3:
        return float("nan"), float("nan")
    slope, intercept = np.polyfit(np.log(1.0 / P[pos]), np.log(dev[pos]), 1)
    A = float(np.exp(intercept))
    return float(slope), A


# =====================================================================
# R1
# =====================================================================
def R1_reliability_seeds(N: int = 21, n_seeds: int = 80):
    """Compute β across many random α profiles. Report median + 90 % band."""
    print("=" * 70)
    print(f"R1)  Reliability across {n_seeds} random α profiles, N = {N}")
    print("=" * 70)
    omega = DEFAULT_OMEGA
    rng = np.random.default_rng(2026)
    betas = np.zeros(n_seeds)
    devs_mat = np.zeros((n_seeds, len(PERIODS)))
    for s in range(n_seeds):
        omega0_arr = 2.10 * np.pi + rng.uniform(-0.10, 0.10, size=N) * np.pi
        alphas = np.array([
            cda.LorentzAlpha(omega0=w0, gamma=DEFAULT_GAMMA, F=DEFAULT_F)(omega=omega)
            for w0 in omega0_arr
        ], dtype=complex)
        for i, p in enumerate(PERIODS):
            devs_mat[s, i] = _mean_dev_nonuniform(N, p, alphas)
        betas[s], _ = _fit_beta(PERIODS, devs_mat[s])

    median_beta = float(np.median(betas))
    p5_beta = float(np.percentile(betas, 5))
    p95_beta = float(np.percentile(betas, 95))
    print(f"  β: median = {median_beta:.3f},  90% band = [{p5_beta:.3f}, {p95_beta:.3f}]")

    fig, axs = plt.subplots(1, 2, figsize=(13, 5.0))
    # left: histogram of β
    axs[0].hist(betas, bins=20, color="#1A478A", alpha=0.7, edgecolor="black")
    axs[0].axvline(median_beta, color="#C0392B", lw=2,
                   label=f"median β = {median_beta:.2f}")
    axs[0].axvspan(p5_beta, p95_beta, color="#C0392B", alpha=0.15,
                   label=f"90 % band [{p5_beta:.2f}, {p95_beta:.2f}]")
    axs[0].set_xlabel(r"fitted exponent β")
    axs[0].set_ylabel("count")
    axs[0].set_title(f"R1)  Distribution of β across {n_seeds} random α profiles")
    axs[0].grid(alpha=0.3)
    axs[0].legend()

    # right: median curve with band
    p5_dev = np.percentile(devs_mat, 5, axis=0)
    p95_dev = np.percentile(devs_mat, 95, axis=0)
    median_dev = np.median(devs_mat, axis=0)
    axs[1].fill_between(PERIODS, p5_dev, p95_dev, color="#C0392B", alpha=0.25,
                        label="90 % band")
    axs[1].plot(PERIODS, median_dev, "o-", color="#C0392B", lw=2,
                label="median Δφ̄")
    axs[1].set_xlabel(r"period $P$ (units of $\lambda$)")
    axs[1].set_ylabel(r"mean $|\Delta\varphi|$ (deg)")
    axs[1].set_title("R1)  Reliability bands of the increase law")
    axs[1].grid(alpha=0.3)
    axs[1].legend()
    fig.tight_layout()
    out = os.path.join(FIG_DIR, "reliability_seeds.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"  figure: {out}\n")
    return {"n_seeds": n_seeds, "median_beta": median_beta,
            "p5_beta": p5_beta, "p95_beta": p95_beta,
            "median_dev_curve": median_dev.tolist(),
            "p5_dev_curve": p5_dev.tolist(),
            "p95_dev_curve": p95_dev.tolist(),
            "figure": out}


# =====================================================================
# R2
# =====================================================================
def R2_grading_magnitude(N: int = 21):
    """How does the magnitude of α-grading change Δφ̄(P)?"""
    print("=" * 70)
    print(f"R2)  Grading magnitude sensitivity, N = {N}")
    print("=" * 70)
    widths = [0.00, 0.05, 0.10, 0.20, 0.30, 0.40]
    omega = DEFAULT_OMEGA
    cmap = plt.cm.plasma
    fig, ax = plt.subplots(figsize=(9, 5.5))
    rows = []
    for k, w in enumerate(widths):
        if w == 0.0:
            # uniform reference
            dev = np.array([_mean_dev_uniform(N, p) for p in PERIODS])
            label = "uniform (w = 0)"
        else:
            omega0_arr = np.linspace((2.10 - w / 2.0) * np.pi,
                                     (2.10 + w / 2.0) * np.pi, N)
            alphas = np.array([
                cda.LorentzAlpha(omega0=w0, gamma=DEFAULT_GAMMA, F=DEFAULT_F)(omega=omega)
                for w0 in omega0_arr
            ], dtype=complex)
            dev = np.array([_mean_dev_nonuniform(N, p, alphas) for p in PERIODS])
            label = fr"$\Delta\omega_0 = {w:.2f}\pi$"
        beta, _ = _fit_beta(PERIODS, dev)
        c = cmap(k / max(1, len(widths) - 1))
        ax.plot(PERIODS, dev, "o-", color=c, lw=1.4, ms=5,
                label=f"{label},  β = {beta:.2f}")
        rows.append({"width_pi": w, "beta": beta,
                     "dev_P_min": float(dev[0]),
                     "dev_P_max": float(dev[-1])})
        print(f"  w = {w:.2f}π:  β = {beta:.3f},  "
              f"Δφ(P={P_MIN}) = {dev[0]:.2f}°,  Δφ(P={P_MAX}) = {dev[-1]:.2f}°")

    ax.set_xlabel(r"period $P$ (units of $\lambda$)")
    ax.set_ylabel(r"mean $|\Delta\varphi|$ (deg)")
    ax.set_title(f"R2)  Grading-magnitude sensitivity  (N = {N})")
    ax.grid(alpha=0.3)
    ax.legend(loc="upper right")
    fig.tight_layout()
    out = os.path.join(FIG_DIR, "reliability_grading_magnitude.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"  figure: {out}\n")
    return {"rows": rows, "figure": out}


# =====================================================================
# R3
# =====================================================================
def R3_N_convergence(period: float = 0.6):
    """Quantitative N-convergence of bulk Δφ̄, and a 1/√N extrapolation
    to the N → ∞ limit."""
    print("=" * 70)
    print(f"R3)  N-convergence and 1/√N extrapolation at P = {period} λ")
    print("=" * 70)
    Ns = np.array([11, 21, 41, 81, 161, 321, 641])
    alpha = default_alpha()
    mean_dev = []
    for N in Ns:
        res = cda.run_uniform_array(N=int(N), period=period, alpha=alpha)
        mean_dev.append(float(np.degrees(res["mean_phase_dev"])))
    mean_dev = np.array(mean_dev)

    # Fit  y(N) = y_inf + B / sqrt(N)
    inv_sqrtN = 1.0 / np.sqrt(Ns)
    slope, y_inf = np.polyfit(inv_sqrtN, mean_dev, 1)
    print(f"  Fit  Δφ̄(N) ≈ {y_inf:.3f}° + {slope:.3f}° · (1/√N)")
    print(f"  Extrapolated N → ∞ limit  ≈ {y_inf:.3f}°")

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.plot(Ns, mean_dev, "o", color="#1A478A", ms=8, label="CDA simulation")
    Ns_smooth = np.linspace(Ns.min(), 2000, 200)
    ax.plot(Ns_smooth, y_inf + slope / np.sqrt(Ns_smooth),
            "-", color="#C0392B", lw=2,
            label=fr"fit  $y_\infty + B/\sqrt{{N}}$:  $y_\infty$ = {y_inf:.2f}°, B = {slope:.2f}°")
    ax.axhline(y_inf, color="#1E8A4C", linestyle="--",
               label=f"N → ∞ limit = {y_inf:.2f}°")
    ax.set_xscale("log")
    ax.set_xlabel("array size  N")
    ax.set_ylabel(r"mean $|\Delta\varphi|$ (deg)")
    ax.set_title(f"R3)  N-convergence at P = {period} λ")
    ax.grid(alpha=0.3, which="both")
    ax.legend()
    fig.tight_layout()
    out = os.path.join(FIG_DIR, "reliability_N_convergence.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"  figure: {out}\n")
    return {"Ns": Ns.tolist(), "mean_dev_deg": mean_dev.tolist(),
            "y_inf_extrapolated": float(y_inf), "slope_B": float(slope),
            "figure": out}


# =====================================================================
# Main
# =====================================================================
def main():
    R1 = R1_reliability_seeds(N=21, n_seeds=80)
    R2 = R2_grading_magnitude(N=21)
    R3 = R3_N_convergence(period=0.6)
    summary = {"R1": R1, "R2": R2, "R3": R3}
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"summary saved: {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
