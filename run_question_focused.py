"""
Focused, quantitative answer to the central research question.

    "How does mean |Δφ| INCREASE as the array period P DECREASES?"

We work in the sub-wavelength window P ∈ [0.55, 0.85] λ, which is
physically relevant for metasurface design and excludes the Wood-
anomaly singularity at P = λ.

Nine analyses:

    Q1.  Fine sweep + parametric fits (power law & linear in 1/P)
    Q2.  Array-size N dependence of the fit
    Q3.  Grading-width sensitivity (non-uniform array)
    Q4.  Reliability across 50 random α profiles
    Q5.  FDTD comparison restricted to the sub-λ window
    Q6.  Log-log direct β measurement with regression uncertainty
    Q7.  Comparison with the analytic 2D lattice sum
    Q8.  Coupling-strength F sensitivity
    Q9.  β across multiple fit windows

Outputs are JSON (`week3_question_summary.json`) + figures in `figures/`.
"""

from __future__ import annotations

import os
import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

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
SUMMARY_PATH = os.path.join(HERE, "week3_question_summary.json")
FDTD_DATA_PATH = os.path.join(HERE, "fdtd_results", "fdtd_data.json")

P_MIN, P_MAX = 0.55, 0.85
N_POINTS = 31
PERIODS_FINE = np.linspace(P_MIN, P_MAX, N_POINTS)


def graded_alphas(N, omega0_min=2.00 * np.pi, omega0_max=2.20 * np.pi):
    omega = DEFAULT_OMEGA
    omega0_array = np.linspace(omega0_min, omega0_max, N)
    return np.array([
        cda.LorentzAlpha(omega0=w0, gamma=DEFAULT_GAMMA, F=DEFAULT_F)(omega=omega)
        for w0 in omega0_array
    ], dtype=complex)


def mean_dev_uniform(N, period):
    return float(np.degrees(cda.run_uniform_array(N=N, period=period, alpha=default_alpha())["mean_phase_dev"]))


def mean_dev_nonuniform(N, period, alphas):
    pos = cda.linear_array(N, period)
    return float(np.degrees(cda.run_nonuniform_array(positions=pos, alphas=alphas)["mean_phase_dev"]))


def power_law(P, A, beta):
    return A * (1.0 / P) ** beta


def linear_inv(P, a, b):
    return a + b * (1.0 / P)


def _r2(y, y_fit):
    ss_res = float(np.sum((y - y_fit) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    return 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")


def fit_both(P, dev):
    """Power law via log-log linear regression + linear-in-(1/P)."""
    P_arr = np.asarray(P, dtype=float)
    dev_arr = np.asarray(dev, dtype=float)
    pos = dev_arr > 0
    if pos.sum() >= 3:
        slope, intercept = np.polyfit(np.log(1.0 / P_arr[pos]),
                                      np.log(dev_arr[pos]), 1)
        A_p, beta = float(np.exp(intercept)), float(slope)
        r2_p = _r2(dev_arr[pos], power_law(P_arr[pos], A_p, beta))
        popt_p = (A_p, beta)
    else:
        popt_p, r2_p = None, float("nan")
    try:
        popt_l, _ = curve_fit(linear_inv, P_arr, dev_arr,
                              p0=(np.mean(dev_arr), 1.0), maxfev=5000)
        r2_l = _r2(dev_arr, linear_inv(P_arr, *popt_l))
    except RuntimeError:
        popt_l, r2_l = None, float("nan")
    return {"power": (popt_p, r2_p), "linear_inv": (popt_l, r2_l)}


# =====================================================================
# Q1
# =====================================================================
def Q1_fine_sweep(N=21):
    print("=" * 70)
    print(f"Q1)  Fine sub-wavelength sweep  P ∈ [{P_MIN}, {P_MAX}] λ,  N = {N}")
    print("=" * 70)
    P = PERIODS_FINE
    dev = np.array([mean_dev_uniform(N=N, period=p) for p in P])
    fits = fit_both(P, dev)
    popt_p, r2_p = fits["power"]
    popt_l, r2_l = fits["linear_inv"]
    if popt_p is not None:
        print(f"  Δφ(P) ≈ {popt_p[0]:.3f} · (λ/P)^{popt_p[1]:.3f}     R² = {r2_p:.3f}")
    if popt_l is not None:
        print(f"  Δφ(P) ≈ {popt_l[0]:.3f} + {popt_l[1]:.3f}·(λ/P)     R² = {r2_l:.3f}")

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.plot(P, dev, "o", color="#1A478A", ms=7, label="CDA simulation", zorder=3)
    P_smooth = np.linspace(P.min(), P.max(), 200)
    if popt_p is not None:
        ax.plot(P_smooth, power_law(P_smooth, *popt_p), "-",
                color="#C0392B", lw=2,
                label=fr"power law $A(\lambda/P)^\beta$, β={popt_p[1]:.2f}, R²={r2_p:.3f}")
    if popt_l is not None:
        ax.plot(P_smooth, linear_inv(P_smooth, *popt_l), "--",
                color="#1E8A4C", lw=2,
                label=fr"linear in 1/P,  slope={popt_l[1]:.2f}°·P/λ, R²={r2_l:.3f}")
    ax.annotate("", xy=(P_MIN, dev[0] * 0.9), xytext=(P_MAX, dev[0] * 0.9),
                arrowprops=dict(arrowstyle="->", color="#888", lw=1.5))
    ax.text((P_MIN + P_MAX) / 2, dev[0] * 0.83, "P decreases",
            color="#666", ha="center", fontsize=10)
    ax.set_xlabel(r"period $P$  (units of $\lambda$)")
    ax.set_ylabel(r"mean $|\Delta\varphi|$  (deg)")
    ax.set_title(f"Q1)  Sub-wavelength increase law  (N = {N}, off-resonance)")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    out = os.path.join(FIG_DIR, "Q_main_subwavelength_sweep.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"  figure: {out}\n")
    return {
        "periods": P.tolist(),
        "dev_deg": dev.tolist(),
        "power": (list(popt_p) if popt_p is not None else None, float(r2_p)),
        "linear_inv": (list(popt_l) if popt_l is not None else None, float(r2_l)),
    }


# =====================================================================
# Q2
# =====================================================================
def Q2_N_dependence():
    print("=" * 70)
    print("Q2)  Array-size dependence")
    print("=" * 70)
    Ns = [11, 21, 41, 81]
    colors = ["#1A478A", "#2E6BB0", "#5D9CEC", "#8DC9FF"]
    P = PERIODS_FINE
    fig, ax = plt.subplots(figsize=(9, 5.5))
    rows = []
    for c, N in zip(colors, Ns):
        dev = np.array([mean_dev_uniform(N=N, period=p) for p in P])
        popt_p, r2 = fit_both(P, dev)["power"]
        beta = float(popt_p[1]) if popt_p else float("nan")
        ax.plot(P, dev, "o-", color=c, ms=5, lw=1.4,
                label=f"N = {N},  β = {beta:.2f},  R² = {r2:.3f}")
        rows.append({"N": N, "beta": beta, "R2": float(r2),
                     "dev_at_P_min": float(dev[0]),
                     "dev_at_P_max": float(dev[-1])})
        print(f"  N = {N:>3}: β = {beta:.3f}, R² = {r2:.3f},  "
              f"Δφ(P={P_MIN}) = {dev[0]:.2f}°, Δφ(P={P_MAX}) = {dev[-1]:.2f}°")
    ax.set_xlabel(r"period $P$  (units of $\lambda$)")
    ax.set_ylabel(r"mean $|\Delta\varphi|$  (deg)")
    ax.set_title("Q2)  Array-size dependence")
    ax.grid(alpha=0.3)
    ax.legend(title="N & fitted β")
    fig.tight_layout()
    out = os.path.join(FIG_DIR, "Q_N_dependence.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"  figure: {out}\n")
    return rows


# =====================================================================
# Q3
# =====================================================================
def Q3_grading_width(N=21):
    print("=" * 70)
    print("Q3)  α-grading width sensitivity")
    print("=" * 70)
    widths = [0.05, 0.10, 0.20, 0.40]
    colors = ["#C0392B", "#D55E00", "#E69F00", "#F0E442"]
    P = PERIODS_FINE
    fig, ax = plt.subplots(figsize=(9, 5.5))
    rows = []
    for c, w in zip(colors, widths):
        alphas = graded_alphas(N,
                               omega0_min=(2.10 - w / 2.0) * np.pi,
                               omega0_max=(2.10 + w / 2.0) * np.pi)
        dev = np.array([mean_dev_nonuniform(N=N, period=p, alphas=alphas) for p in P])
        popt_p, r2 = fit_both(P, dev)["power"]
        beta = float(popt_p[1]) if popt_p else float("nan")
        ax.plot(P, dev, "o-", color=c, ms=5, lw=1.4,
                label=fr"$\Delta\omega_0 = {w:.2f}\pi$,  β = {beta:.2f}")
        rows.append({"width_pi": w, "beta": beta, "R2": float(r2),
                     "dev_at_P_min": float(dev[0])})
        print(f"  Δω₀ = {w:.2f}π: β = {beta:.3f}, R² = {r2:.3f},  Δφ(P={P_MIN}) = {dev[0]:.2f}°")
    dev_u = np.array([mean_dev_uniform(N=N, period=p) for p in P])
    ax.plot(P, dev_u, "k--", lw=1.6, label="uniform (reference)")
    ax.set_xlabel(r"period $P$  (units of $\lambda$)")
    ax.set_ylabel(r"mean $|\Delta\varphi|$  (deg)")
    ax.set_title(f"Q3)  Effect of α-grading width  (N = {N})")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    out = os.path.join(FIG_DIR, "Q_grading_width.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"  figure: {out}\n")
    return rows


# =====================================================================
# Q4
# =====================================================================
def Q4_reliability(N=21, n_seeds=50):
    print("=" * 70)
    print(f"Q4)  Reliability across {n_seeds} random α profiles")
    print("=" * 70)
    rng = np.random.default_rng(123)
    omega = DEFAULT_OMEGA
    P = PERIODS_FINE
    mat = np.zeros((n_seeds, len(P)))
    for s in range(n_seeds):
        omega0_arr = 2.10 * np.pi + rng.uniform(-0.10, 0.10, size=N) * np.pi
        alphas = np.array([
            cda.LorentzAlpha(omega0=w0, gamma=DEFAULT_GAMMA, F=DEFAULT_F)(omega=omega)
            for w0 in omega0_arr
        ], dtype=complex)
        for i, p in enumerate(P):
            mat[s, i] = mean_dev_nonuniform(N, p, alphas)

    median = np.median(mat, axis=0)
    p5 = np.percentile(mat, 5, axis=0)
    p95 = np.percentile(mat, 95, axis=0)
    print(f"  median Δφ(P={P_MIN}) = {median[0]:.2f}°,  P={P_MAX} = {median[-1]:.2f}°")
    print(f"  90% band P={P_MIN} : [{p5[0]:.2f}, {p95[0]:.2f}]°")
    print(f"  90% band P={P_MAX}: [{p5[-1]:.2f}, {p95[-1]:.2f}]°")
    popt_p, r2 = fit_both(P, median)["power"]
    beta_med = float(popt_p[1]) if popt_p else float("nan")
    print(f"  median fit:  β = {beta_med:.3f},  R² = {r2:.3f}")

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.fill_between(P, p5, p95, color="#C0392B", alpha=0.25,
                    label=f"90 % band over {n_seeds} random profiles")
    ax.plot(P, median, "o-", color="#C0392B", lw=2.0, ms=6,
            label=f"median, β = {beta_med:.2f}, R² = {r2:.3f}")
    dev_u = np.array([mean_dev_uniform(N=N, period=p) for p in P])
    popt_u, r2u = fit_both(P, dev_u)["power"]
    beta_u = float(popt_u[1]) if popt_u else float("nan")
    ax.plot(P, dev_u, "s-", color="#1A478A", lw=1.6, ms=5,
            label=f"uniform, β = {beta_u:.2f}, R² = {r2u:.3f}")
    ax.set_xlabel(r"period $P$  (units of $\lambda$)")
    ax.set_ylabel(r"mean $|\Delta\varphi|$  (deg)")
    ax.set_title(f"Q4)  Reliability across random α  (N = {N})")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    out = os.path.join(FIG_DIR, "Q_reliability_bands.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"  figure: {out}\n")
    return {
        "median_beta": beta_med, "median_R2": float(r2),
        "uniform_beta": beta_u,
        "median_at_P_min": float(median[0]),
        "median_at_P_max": float(median[-1]),
        "p5_band": p5.tolist(), "p95_band": p95.tolist(),
    }


# =====================================================================
# Q5
# =====================================================================
def Q5_fdtd_comparison():
    print("=" * 70)
    print("Q5)  FDTD vs CDA inside the sub-wavelength window")
    print("=" * 70)
    if not os.path.exists(FDTD_DATA_PATH):
        print("  FDTD data not found. Skipping.\n")
        return None
    with open(FDTD_DATA_PATH, "r", encoding="utf-8") as f:
        fdtd = json.load(f)
    Pf = np.array(fdtd["period_lambdas"])
    ref = fdtd["isolated_phase_rad"]
    sub_mask = (Pf >= P_MIN) & (Pf <= P_MAX)
    Psub = Pf[sub_mask]
    fdtd_means = []
    for P in Psub:
        ph = np.array(fdtd["phases"][f"{P:.3f}"])
        dev = np.angle(np.exp(1j * (ph - ref)))
        fdtd_means.append(float(np.degrees(np.mean(np.abs(dev)))))
    fdtd_means = np.array(fdtd_means)

    N_fdtd = 11
    cda_means = np.array([mean_dev_uniform(N=N_fdtd, period=p) for p in Psub])

    P = PERIODS_FINE
    dev_fine = np.array([mean_dev_uniform(N=N_fdtd, period=p) for p in P])
    popt_p, r2 = fit_both(P, dev_fine)["power"]

    fig, ax = plt.subplots(figsize=(9, 5.5))
    P_smooth = np.linspace(P_MIN, P_MAX, 200)
    if popt_p is not None:
        ax.plot(P_smooth, power_law(P_smooth, *popt_p), "-",
                color="#1A478A", lw=1.8, alpha=0.8,
                label=fr"CDA fine-fit  β = {popt_p[1]:.2f}, R²={r2:.3f}")
    ax.plot(Psub, cda_means, "o", color="#1A478A", ms=9,
            label=f"CDA at FDTD points (N = {N_fdtd})")
    ax.plot(Psub, fdtd_means, "s", color="#C0392B", ms=9,
            label="FDTD measurement")
    ax.set_xlabel(r"period $P$  (units of $\lambda$)")
    ax.set_ylabel(r"mean $|\Delta\varphi|$  (deg)")
    ax.set_title(f"Q5)  Sub-wavelength CDA ↔ FDTD agreement  (N = {N_fdtd})")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    out = os.path.join(FIG_DIR, "Q_fdtd_comparison_subwavelength.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)
    diffs = fdtd_means - cda_means
    rms = float(np.sqrt(np.mean(diffs ** 2)))
    print(f"  CDA - FDTD diffs: {diffs}")
    print(f"  RMS = {rms:.3f}°")
    print(f"  figure: {out}\n")
    return {
        "subwavelength_periods": Psub.tolist(),
        "cda_means": cda_means.tolist(),
        "fdtd_means": fdtd_means.tolist(),
        "rms_diff_deg": rms,
    }


# =====================================================================
# Q6
# =====================================================================
def Q6_loglog(N=21):
    print("=" * 70)
    print("Q6)  Log-log analysis — direct β with regression uncertainty")
    print("=" * 70)
    P = PERIODS_FINE
    dev = np.array([mean_dev_uniform(N=N, period=p) for p in P])
    log_inv = np.log(1.0 / P)
    log_dev = np.log(dev)
    coeffs, cov = np.polyfit(log_inv, log_dev, 1, cov=True)
    slope, intercept = coeffs[0], coeffs[1]
    sigma = float(np.sqrt(cov[0, 0]))
    A_fit = float(np.exp(intercept))
    r2 = _r2(log_dev, slope * log_inv + intercept)
    print(f"  β = {slope:.3f} ± {sigma:.3f},  A = {A_fit:.3f},  R²(log) = {r2:.3f}")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    P_smooth = np.linspace(P.min(), P.max(), 200)
    ax1.plot(P, dev, "o", color="#1A478A", ms=7, label="CDA")
    ax1.plot(P_smooth, A_fit * (1.0 / P_smooth) ** slope, "-",
             color="#C0392B", lw=2,
             label=fr"$A(\lambda/P)^\beta$, β={slope:.2f}")
    ax1.set_xlabel(r"period $P$ (units of $\lambda$)")
    ax1.set_ylabel(r"mean $|\Delta\varphi|$ (deg)")
    ax1.set_title("Linear scale")
    ax1.grid(alpha=0.3)
    ax1.legend()

    ax2.loglog(1.0 / P, dev, "o", color="#1A478A", ms=7, label="CDA")
    ax2.loglog(1.0 / P_smooth, A_fit * (1.0 / P_smooth) ** slope, "-",
               color="#C0392B", lw=2,
               label=fr"slope β = {slope:.2f} ± {sigma:.2f}")
    ax2.set_xlabel(r"$\lambda/P$ (log)")
    ax2.set_ylabel(r"$|\Delta\varphi|$ (deg, log)")
    ax2.set_title(f"Log-log:  R² = {r2:.3f}")
    ax2.grid(alpha=0.3, which="both")
    ax2.legend()
    fig.suptitle(f"Q6)  Direct β measurement  β = {slope:.2f} ± {sigma:.2f}  (N = {N})",
                 fontsize=13)
    fig.tight_layout()
    out = os.path.join(FIG_DIR, "Q_loglog_analysis.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"  figure: {out}\n")
    return {"beta": float(slope), "beta_sigma": sigma,
            "A_deg": A_fit, "R2_log": float(r2)}


# =====================================================================
# Q7
# =====================================================================
def Q7_lattice_sum(N=21):
    print("=" * 70)
    print("Q7)  Lattice-sum comparison")
    print("=" * 70)
    P = PERIODS_FINE
    half = (N - 1) // 2
    Sabs = np.zeros_like(P)
    Sim = np.zeros_like(P)
    Sre = np.zeros_like(P)
    for i, p in enumerate(P):
        rs = np.arange(1, half + 1) * p
        S = np.sum(cda.greens_2d(rs))
        Sabs[i] = float(np.abs(S))
        Sim[i] = float(np.imag(S))
        Sre[i] = float(np.real(S))
    dev = np.array([mean_dev_uniform(N=N, period=p) for p in P])

    slope_dev, _ = np.polyfit(np.log(1.0 / P), np.log(dev), 1)
    if Sim.min() > 0:
        slope_S, _ = np.polyfit(np.log(1.0 / P), np.log(Sim), 1)
    else:
        slope_S, _ = np.polyfit(np.log(1.0 / P), np.log(np.abs(Sim) + 1e-30), 1)
    print(f"  Δφ slope vs (λ/P) = {slope_dev:.3f}")
    print(f"  Im[ΣG] slope vs (λ/P) = {slope_S:.3f}")

    fig, axs = plt.subplots(1, 2, figsize=(13, 5))
    axA = axs[0]
    axA.plot(P, dev, "o-", color="#1A478A", lw=2, label=fr"|Δφ|, β={slope_dev:.2f}")
    axB = axA.twinx()
    axB.plot(P, Sim, "s--", color="#C0392B", lw=2,
             label=fr"Im[Σ G(jP)], β={slope_S:.2f}")
    axA.set_xlabel(r"period $P$ (units of $\lambda$)")
    axA.set_ylabel("|Δφ| (deg)", color="#1A478A")
    axA.tick_params(axis="y", colors="#1A478A")
    axB.set_ylabel("Im[Σ G(jP)]", color="#C0392B")
    axB.tick_params(axis="y", colors="#C0392B")
    axA.set_title("CDA |Δφ| vs Im[lattice sum]")
    axA.grid(alpha=0.3)
    h1, l1 = axA.get_legend_handles_labels()
    h2, l2 = axB.get_legend_handles_labels()
    axA.legend(h1 + h2, l1 + l2, loc="upper right")

    axC = axs[1]
    axC.plot(P, Sabs, "o-", color="#444", lw=1.4, label="|Σ G(jP)|")
    axC.plot(P, Sim, "s-", color="#C0392B", lw=1.4, label="Im[Σ G(jP)]")
    axC.plot(P, Sre, "^-", color="#1A478A", lw=1.4, label="Re[Σ G(jP)]")
    axC.axhline(0, color="k", lw=0.6)
    axC.set_xlabel(r"period $P$ (units of $\lambda$)")
    axC.set_ylabel("Σ G(jP)")
    axC.set_title("Hankel sum components")
    axC.grid(alpha=0.3)
    axC.legend()
    fig.suptitle(f"Q7)  Why  β ≈ 1 ?   Radiative lattice sum drives Δφ  (N = {N})")
    fig.tight_layout()
    out = os.path.join(FIG_DIR, "Q_lattice_sum_comparison.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"  figure: {out}\n")
    return {"slope_dev": float(slope_dev), "slope_Sim": float(slope_S)}


# =====================================================================
# Q8
# =====================================================================
def Q8_F_sensitivity(N=21):
    print("=" * 70)
    print("Q8)  Polarizability strength F sensitivity")
    print("=" * 70)
    omega = DEFAULT_OMEGA
    P = PERIODS_FINE
    F_values = [0.5, 1.0, 2.0, 4.0, 8.0]
    fig, ax = plt.subplots(figsize=(9, 5.5))
    rows = []
    cmap = plt.cm.viridis
    for k, F in enumerate(F_values):
        alpha = cda.LorentzAlpha(omega0=DEFAULT_OMEGA0, gamma=DEFAULT_GAMMA, F=F)(omega=omega)
        dev = np.array([np.degrees(cda.run_uniform_array(N=N, period=p, alpha=alpha)["mean_phase_dev"]) for p in P])
        slope, intercept = np.polyfit(np.log(1.0 / P), np.log(dev), 1)
        c = cmap(k / max(1, len(F_values) - 1))
        ax.plot(P, dev, "o-", color=c, ms=5, label=f"F = {F:.1f},  β = {slope:.2f}")
        rows.append({"F": F, "beta": float(slope),
                     "dev_at_P_min": float(dev[0]), "dev_at_P_max": float(dev[-1])})
        print(f"  F = {F:>4.1f}:  β = {slope:.3f},  "
              f"Δφ(P={P_MIN}) = {dev[0]:.2f}°,  Δφ(P={P_MAX}) = {dev[-1]:.2f}°")
    ax.set_xlabel(r"period $P$ (units of $\lambda$)")
    ax.set_ylabel(r"mean $|\Delta\varphi|$ (deg)")
    ax.set_title(f"Q8)  Coupling-strength F sensitivity  (N = {N})")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    out = os.path.join(FIG_DIR, "Q_F_sensitivity.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"  figure: {out}\n")
    return rows


# =====================================================================
# Q9
# =====================================================================
def Q9_multi_windows(N=21):
    print("=" * 70)
    print("Q9)  β across multiple windows")
    print("=" * 70)
    windows = [(0.55, 0.85), (0.55, 0.80), (0.60, 0.85), (0.60, 0.80), (0.65, 0.85)]
    rows = []
    for (lo, hi) in windows:
        P = np.linspace(lo, hi, 31)
        dev = np.array([mean_dev_uniform(N=N, period=p) for p in P])
        coeffs, cov = np.polyfit(np.log(1.0 / P), np.log(dev), 1, cov=True)
        slope, sig = float(coeffs[0]), float(np.sqrt(cov[0, 0]))
        r2 = _r2(np.log(dev), slope * np.log(1.0 / P) + coeffs[1])
        rows.append({"window": (lo, hi), "beta": slope, "beta_sigma": sig, "R2_log": float(r2)})
        print(f"  P ∈ [{lo:.2f}, {hi:.2f}]:  β = {slope:.2f} ± {sig:.2f},  R² = {r2:.3f}")

    fig, ax = plt.subplots(figsize=(9, 5.0))
    labels = [f"[{w['window'][0]:.2f},{w['window'][1]:.2f}]" for w in rows]
    betas = [w["beta"] for w in rows]
    sigs = [w["beta_sigma"] for w in rows]
    xs = np.arange(len(rows))
    ax.errorbar(xs, betas, yerr=sigs, fmt="s", color="#1A478A", ms=10, capsize=6, lw=1.5)
    ax.axhline(1.0, color="#888", linestyle="--", alpha=0.6, label="β = 1 (perfect 1/P)")
    ax.axhline(float(np.mean(betas)), color="#C0392B", linestyle=":",
               label=f"mean β = {np.mean(betas):.2f}")
    ax.set_xticks(xs)
    ax.set_xticklabels(labels, rotation=15)
    ax.set_xlabel("fit window  P/λ")
    ax.set_ylabel(r"fitted exponent  β")
    ax.set_title(f"Q9)  β across windows  (N = {N})")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    out = os.path.join(FIG_DIR, "Q_multi_windows.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"  figure: {out}\n")
    return {"windows": rows, "mean_beta": float(np.mean(betas))}


# =====================================================================
# Main
# =====================================================================
def main():
    Q1 = Q1_fine_sweep(N=21)
    Q2 = Q2_N_dependence()
    Q3 = Q3_grading_width(N=21)
    Q4 = Q4_reliability(N=21, n_seeds=50)
    Q5 = Q5_fdtd_comparison()
    Q6 = Q6_loglog(N=21)
    Q7 = Q7_lattice_sum(N=21)
    Q8 = Q8_F_sensitivity(N=21)
    Q9 = Q9_multi_windows(N=21)
    summary = {"Q1": Q1, "Q2": Q2, "Q3": Q3, "Q4": Q4, "Q5": Q5,
               "Q6": Q6, "Q7": Q7, "Q8": Q8, "Q9": Q9}
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"summary saved: {SUMMARY_PATH}\n")

    A_uni, beta_uni = (Q1["power"][0] or (float("nan"), float("nan")))
    a_lin, b_lin = (Q1["linear_inv"][0] or (float("nan"), float("nan")))
    print("=" * 70)
    print("ANSWER to the central question:")
    print("=" * 70)
    print(f"  |Δφ|(P)  ≈  {A_uni:.3f} · (λ/P)^{beta_uni:.2f}      "
          f"R² = {Q1['power'][1]:.3f}")
    print(f"  |Δφ|(P)  ≈  {a_lin:.3f} + {b_lin:.3f} · (λ/P)        "
          f"R² = {Q1['linear_inv'][1]:.3f}")
    print(f"  P = {P_MAX} λ   →   |Δφ| = {Q1['dev_deg'][-1]:.2f}°")
    print(f"  P = {P_MIN} λ   →   |Δφ| = {Q1['dev_deg'][0]:.2f}°")
    print(f"  ratio = {Q1['dev_deg'][0] / Q1['dev_deg'][-1]:.2f}×")


if __name__ == "__main__":
    main()
