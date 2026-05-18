"""
Controlled comparison analyses (Result A — F).

  A. Off-resonance fine sweep:        uniform vs non-uniform mean |Δφ|(P)
  B. Threshold periods P*:            P at which mean |Δφ| < threshold
  C. Per-atom phase profile:          mirror-symmetry break in graded arrays
  D. Matrix conditioning vs P:        Wood-anomaly is NOT singularity
  E. Optical-theorem energy budget:   P_sca / P_ext stays in [0, 1]
  F. α-ordering sensitivity:          smooth gradient is coupling-tolerant
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
SUMMARY_PATH = os.path.join(HERE, "week3_summary.json")


def graded_alphas(N: int,
                  omega0_min: float = 2.00 * np.pi,
                  omega0_max: float = 2.20 * np.pi) -> np.ndarray:
    omega = DEFAULT_OMEGA
    omega0_array = np.linspace(omega0_min, omega0_max, N)
    return np.array([
        cda.LorentzAlpha(omega0=w0, gamma=DEFAULT_GAMMA, F=DEFAULT_F)(omega=omega)
        for w0 in omega0_array
    ], dtype=complex)


# =====================================================================
# A
# =====================================================================
def part_A_offresonance_sweep(N: int = 31):
    print("=" * 70)
    print("A) Off-resonance fine sweep:  uniform vs non-uniform")
    print("=" * 70)

    periods = np.linspace(0.5, 3.0, 251)
    alpha_u = default_alpha()
    alphas_n = graded_alphas(N)

    dev_u = np.zeros_like(periods)
    dev_n = np.zeros_like(periods)
    for i, P in enumerate(periods):
        pos = cda.linear_array(N, P)
        ru = cda.run_uniform_array(N=N, period=P, alpha=alpha_u)
        rn = cda.run_nonuniform_array(positions=pos, alphas=alphas_n)
        dev_u[i] = np.degrees(ru["mean_phase_dev"])
        dev_n[i] = np.degrees(rn["mean_phase_dev"])

    band = 0.03
    mask = np.ones_like(periods, dtype=bool)
    for m in [1.0, 2.0, 3.0]:
        mask &= np.abs(periods - m) > band

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.5))
    ax1.plot(periods, dev_u, color="#1A478A", lw=1.4, alpha=0.4)
    ax1.plot(periods, dev_n, color="#C0392B", lw=1.4, alpha=0.4)
    ax1.plot(periods[mask], dev_u[mask], "o", color="#1A478A",
             ms=2.5, label="Uniform (off-resonance)")
    ax1.plot(periods[mask], dev_n[mask], "s", color="#C0392B",
             ms=2.5, label="Non-uniform (off-resonance)")
    for m in [1.0, 2.0, 3.0]:
        ax1.axvspan(m - band, m + band, color="gray", alpha=0.2)
    ax1.set_xlabel(r"period $P$  (units of $\lambda$)")
    ax1.set_ylabel(r"mean $|\Delta\varphi|$  (deg)")
    ax1.set_title(f"A) Mean phase deviation vs period  (N = {N})")
    ax1.set_ylim(0, 35)
    ax1.grid(alpha=0.3)
    ax1.legend()

    ax2.plot(periods, dev_n - dev_u, color="#1E8A4C", lw=1.4)
    ax2.axhline(0, color="k", lw=0.6)
    for m in [1.0, 2.0, 3.0]:
        ax2.axvspan(m - band, m + band, color="gray", alpha=0.2)
    ax2.set_xlabel(r"period $P$  (units of $\lambda$)")
    ax2.set_ylabel(r"non-uniform − uniform  (deg)")
    ax2.set_title("A) Extra distortion from α-inhomogeneity")
    ax2.set_ylim(-15, 15)
    ax2.grid(alpha=0.3)

    fig.tight_layout()
    out = os.path.join(FIG_DIR, "week3_A_offresonance_sweep.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)
    off_u = float(np.mean(dev_u[mask]))
    off_n = float(np.mean(dev_n[mask]))
    extra = off_n - off_u
    print(f"  off-res mean |Δφ|  uniform    = {off_u:.2f}°")
    print(f"  off-res mean |Δφ|  non-uniform = {off_n:.2f}°")
    print(f"  extra from inhomogeneity      = {extra:+.2f}°")
    print(f"  figure: {out}\n")
    return {
        "periods": periods.tolist(),
        "dev_uniform_deg": dev_u.tolist(),
        "dev_nonuniform_deg": dev_n.tolist(),
        "offres_mean_uniform": off_u,
        "offres_mean_nonuniform": off_n,
        "extra_distortion": extra,
        "figure": out,
    }


# =====================================================================
# B
# =====================================================================
def part_B_threshold(A: dict,
                     thresholds_deg: tuple = (1.0, 2.0, 3.0, 5.0)):
    print("=" * 70)
    print("B) Threshold period P*  (mean |Δφ| sustained below threshold)")
    print("=" * 70)
    P = np.array(A["periods"])
    dev_u = np.array(A["dev_uniform_deg"])
    dev_n = np.array(A["dev_nonuniform_deg"])
    band = 0.03
    mask = np.ones_like(P, dtype=bool)
    for m in [1.0, 2.0, 3.0]:
        mask &= np.abs(P - m) > band

    def find_thr(devs, thr):
        for i in range(len(P)):
            tail = mask[i:]
            if not tail.any():
                continue
            if np.all(devs[i:][tail] < thr):
                return float(P[i])
        return None

    table = []
    for th in thresholds_deg:
        Pu = find_thr(dev_u, th)
        Pn = find_thr(dev_n, th)
        table.append({"threshold_deg": th, "P_star_uniform": Pu,
                      "P_star_nonuniform": Pn})
        ustr = f"{Pu:.3f}" if Pu is not None else " not found"
        nstr = f"{Pn:.3f}" if Pn is not None else " not found"
        print(f"  threshold = {th:>4.1f}°   ->   P*(uniform)={ustr}   "
              f"P*(non-uniform)={nstr}")
    print()
    return {"thresholds": table}


# =====================================================================
# C
# =====================================================================
def part_C_phase_profile(N: int = 31, period: float = 0.7):
    print("=" * 70)
    print("C) Per-atom phase profile (uniform vs non-uniform)")
    print("=" * 70)
    alpha_u = default_alpha()
    alphas_n = graded_alphas(N)
    ru = cda.run_uniform_array(N=N, period=period, alpha=alpha_u)
    pos = cda.linear_array(N, period)
    rn = cda.run_nonuniform_array(positions=pos, alphas=alphas_n)
    dphi_u = np.degrees(cda.phase_deviation(ru["p_coupled"], ru["p_isolated"]))
    dphi_n = np.degrees(cda.phase_deviation(rn["p_coupled"], rn["p_isolated"]))

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(pos, dphi_u, "o-", color="#1A478A", label="Uniform")
    ax.plot(pos, dphi_n, "s-", color="#C0392B", label="Non-uniform (graded α)")
    ax.axhline(0, color="k", lw=0.5)
    ax.set_xlabel(r"atom position $x$  (units of $\lambda$)")
    ax.set_ylabel(r"phase deviation $\Delta\varphi$  (deg)")
    ax.set_title(f"C) Per-atom phase profile  (N = {N}, P = {period} λ)")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    out = os.path.join(FIG_DIR, "week3_C_phase_profile.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)

    mid = N // 2
    asym_u = float(np.mean(dphi_u[:mid]) - np.mean(dphi_u[mid + 1:]))
    asym_n = float(np.mean(dphi_n[:mid]) - np.mean(dphi_n[mid + 1:]))
    print(f"  asymmetry (left − right)  uniform     = {asym_u:+.3f}°")
    print(f"  asymmetry (left − right)  non-uniform = {asym_n:+.3f}°")
    print(f"  figure: {out}\n")
    return {"asymmetry_uniform": asym_u, "asymmetry_nonuniform": asym_n,
            "figure": out}


# =====================================================================
# D
# =====================================================================
def part_D_conditioning(N: int = 31):
    print("=" * 70)
    print("D) Matrix condition number vs period")
    print("=" * 70)
    P = np.linspace(0.5, 3.0, 251)
    alpha = default_alpha()
    cond = np.zeros_like(P)
    for i, p in enumerate(P):
        pos = cda.linear_array(N, p)
        alphas = np.full(N, alpha, dtype=complex)
        A = cda.build_interaction_matrix(pos, alphas)
        cond[i] = np.linalg.cond(A)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.semilogy(P, cond, color="#7E1B8C", lw=1.5)
    for m in [1.0, 2.0, 3.0]:
        ax.axvline(m, color="gray", linestyle="--", alpha=0.5)
    ax.set_xlabel(r"period $P$  (units of $\lambda$)")
    ax.set_ylabel(r"condition number $\kappa(A)$")
    ax.set_title(f"D) Matrix conditioning vs period  (N = {N})")
    ax.grid(alpha=0.3, which="both")
    fig.tight_layout()
    out = os.path.join(FIG_DIR, "week3_D_conditioning.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)

    peaks = []
    for m in [1.0, 2.0, 3.0]:
        local = np.abs(P - m) < 0.10
        if local.any():
            i = np.argmax(cond[local])
            peaks.append((m, float(cond[local][i])))
    print(f"  peaks near integer P: {peaks}")
    print(f"  figure: {out}\n")
    return {"periods": P.tolist(), "cond": cond.tolist(),
            "peaks": peaks, "figure": out}


# =====================================================================
# E
# =====================================================================
def part_E_energy_budget(N: int = 31):
    """
    Energy budget consistency check.

    With the e^{-iωt} convention used by CDA, the standard expressions
    (up to a positive ω/2 factor that cancels in the ratio) are

        P_ext_i = Im( E_inc,i^* · p_i )                    (extinction)
        P_abs_i = Im( p_i · E_loc,i^* ) = |p_i|^2 Im(α_i)/|α_i|^2

    Both are positive for our damped Lorentzian (Im α > 0).

    Note: the order p * conj(E_loc) — equivalent to −Im(p^* · E_loc) —
    is essential.  Using Im(p^* · E_loc) instead gives the wrong sign
    (|p|^2 · Im(1/α) < 0) and is a common pitfall.
    """
    print("=" * 70)
    print("E) Energy budget P_sca / P_ext")
    print("=" * 70)
    P = np.linspace(0.5, 3.0, 121)
    alpha = default_alpha()
    ratio = np.zeros_like(P)
    for i, p in enumerate(P):
        res = cda.run_uniform_array(N=N, period=p, alpha=alpha)
        E_inc = res["E_inc"]
        p_arr = res["p_coupled"]
        E_loc = p_arr / res["alphas"]
        P_ext = float(np.sum(np.imag(np.conj(E_inc) * p_arr)))
        # Correct sign: Im(p · conj(E_loc)) == |p|^2 · Im(α)/|α|^2 > 0
        P_abs = float(np.sum(np.imag(p_arr * np.conj(E_loc))))
        ratio[i] = (P_ext - P_abs) / P_ext if P_ext > 0 else np.nan

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(P, ratio, color="#0E7C66", lw=1.5)
    ax.axhline(0, color="k", lw=0.5)
    ax.axhline(1, color="k", lw=0.5)
    for m in [1.0, 2.0, 3.0]:
        ax.axvline(m, color="gray", linestyle="--", alpha=0.5)
    ax.set_xlabel(r"period $P$  (units of $\lambda$)")
    ax.set_ylabel(r"$P_{sca}/P_{ext}$")
    ax.set_title(f"E) Energy budget  (N = {N})  [1 = lossless, 0 = absorbed]")
    ax.set_ylim(-0.05, 1.1)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    out = os.path.join(FIG_DIR, "week3_E_energy_budget.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"  figure: {out}\n")
    return {"periods": P.tolist(), "Psca_over_Pext": ratio.tolist(),
            "figure": out}


# =====================================================================
# F
# =====================================================================
def part_F_alpha_ordering(N: int = 31, period: float = 0.7):
    print("=" * 70)
    print("F) Sensitivity to α-ordering")
    print("=" * 70)
    omega = DEFAULT_OMEGA
    omega0_arr = np.linspace(2.00 * np.pi, 2.20 * np.pi, N)
    alphas_base = np.array([
        cda.LorentzAlpha(omega0=w0, gamma=DEFAULT_GAMMA, F=DEFAULT_F)(omega=omega)
        for w0 in omega0_arr
    ], dtype=complex)
    pos = cda.linear_array(N, period)

    def md(alphas):
        return float(np.degrees(cda.run_nonuniform_array(positions=pos, alphas=alphas)["mean_phase_dev"]))

    asc = md(alphas_base)
    desc = md(alphas_base[::-1])
    rng = np.random.default_rng(42)
    rd = np.array([md(alphas_base[rng.permutation(N)]) for _ in range(10)])

    print(f"  ascending  : {asc:.3f}°")
    print(f"  descending : {desc:.3f}°")
    print(f"  random shuffles  median = {np.median(rd):.3f}°,  range = [{rd.min():.3f}, {rd.max():.3f}]°")

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar([0, 1], [asc, desc], width=0.4,
           color=["#1A478A", "#C0392B"], label=["ascending", "descending"])
    ax.scatter([2] * len(rd), rd, color="#888", s=30,
               label="10 random shuffles")
    ax.errorbar([2], [np.median(rd)],
                yerr=[[np.median(rd) - rd.min()], [rd.max() - np.median(rd)]],
                color="black", capsize=8, fmt="o", markersize=8,
                label="median + range")
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(["asc.", "desc.", "random"])
    ax.set_ylabel(r"mean $|\Delta\varphi|$  (deg)")
    ax.set_title(f"F) α-ordering sensitivity  (N = {N}, P = {period} λ)")
    ax.grid(alpha=0.3, axis="y")
    ax.legend(loc="upper right")
    fig.tight_layout()
    out = os.path.join(FIG_DIR, "week3_F_alpha_ordering.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"  figure: {out}\n")
    return {
        "ascending_deg": asc, "descending_deg": desc,
        "random_median_deg": float(np.median(rd)),
        "random_min_deg": float(rd.min()),
        "random_max_deg": float(rd.max()),
        "figure": out,
    }


# =====================================================================
# Main
# =====================================================================
def main():
    A = part_A_offresonance_sweep(N=31)
    B = part_B_threshold(A)
    C = part_C_phase_profile(N=31, period=0.7)
    D = part_D_conditioning(N=31)
    E = part_E_energy_budget(N=31)
    F = part_F_alpha_ordering(N=31, period=0.7)

    summary = {
        "A_offres_mean_uniform_deg": A["offres_mean_uniform"],
        "A_offres_mean_nonuniform_deg": A["offres_mean_nonuniform"],
        "A_extra_distortion_deg": A["extra_distortion"],
        "B_thresholds": B["thresholds"],
        "C_asymmetry_uniform_deg": C["asymmetry_uniform"],
        "C_asymmetry_nonuniform_deg": C["asymmetry_nonuniform"],
        "D_conditioning_peaks": D["peaks"],
        "F_ascending_deg": F["ascending_deg"],
        "F_descending_deg": F["descending_deg"],
        "F_random_median_deg": F["random_median_deg"],
        "F_random_range_deg": [F["random_min_deg"], F["random_max_deg"]],
    }
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"summary saved: {SUMMARY_PATH}")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
