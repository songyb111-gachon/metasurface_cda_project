"""
10 independent physical verification tests of the CDA implementation.

   1. Single-dipole sanity check
   2. Two-dipole closed-form coupled solution
   3. Green's function formula + reciprocity G(r) = G(-r)
   4. Linear system residual ||A p − E_inc|| / ||E_inc||
   5. Mirror symmetry of a centred uniform array
   6. Matrix reciprocity A_ij = A_ji
   7. Array-size convergence  (1/√N from 2D Hankel sum)
   8. Wavelength scaling invariance
   9. Extinction power positivity  Im(E_inc* · p) > 0
  10. Non-uniform solver reduces to uniform solver when α is constant
"""

from __future__ import annotations

import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.special import hankel1

import cda
from run_baseline import default_alpha, FIG_DIR

PASS = "PASS"
FAIL = "FAIL"
results: list[tuple[str, str, str]] = []


def report(name: str, ok: bool, detail: str):
    tag = PASS if ok else FAIL
    print(f"[{tag}]  {name}")
    print(f"        {detail}")
    print()
    results.append((tag, name, detail))


# ---------------------------------------------------------------------
# Test 1
# ---------------------------------------------------------------------
def test_single_dipole():
    alpha = default_alpha()
    res = cda.run_uniform_array(N=1, period=1.0, alpha=alpha)
    p_num = res["p_coupled"][0]
    p_ana = alpha * 1.0
    err = abs(p_num - p_ana) / abs(p_ana)
    report(
        "1. Single-dipole sanity check",
        err < 1e-12,
        f"CDA matches analytical p = α · E_inc  (rel. error = {err:.2e})",
    )


# ---------------------------------------------------------------------
# Test 2
# ---------------------------------------------------------------------
def test_two_dipole_analytical(period: float = 0.8):
    alpha = default_alpha()
    G12 = cda.greens_2d(np.array([period]))[0]
    p_ana = alpha / (1.0 - alpha * G12)
    res = cda.run_uniform_array(N=2, period=period, alpha=alpha)
    p1, p2 = res["p_coupled"]
    err1 = abs(p1 - p_ana) / abs(p_ana)
    err2 = abs(p2 - p_ana) / abs(p_ana)
    sym = abs(p1 - p2) / abs(p1)
    report(
        "2. Two-dipole analytical comparison",
        max(err1, err2, sym) < 1e-12,
        f"|p1 - p_ana|/|p_ana| = {err1:.2e},  "
        f"|p2 - p_ana|/|p_ana| = {err2:.2e},  |p1-p2|/|p1| = {sym:.2e}",
    )


# ---------------------------------------------------------------------
# Test 3
# ---------------------------------------------------------------------
def test_green_function():
    rs = np.linspace(0.01, 5.0, 50)
    g = cda.greens_2d(rs)
    g_ref = 0.25j * hankel1(0, 2 * np.pi * rs)
    err_formula = float(np.max(np.abs(g - g_ref)))

    pos = np.array([0.0, 0.7, 1.3, 2.1])
    dx = pos[:, None] - pos[None, :]
    Gmat = cda.greens_2d(np.abs(dx) + 1e-30)
    err_sym = float(np.max(np.abs(Gmat - Gmat.T)))
    report(
        "3. Green's function: formula + symmetry",
        err_formula < 1e-14 and err_sym < 1e-14,
        f"|G(r) − (i/4)H0(k0 r)| max = {err_formula:.2e},  "
        f"max |G_ij − G_ji| = {err_sym:.2e}",
    )


# ---------------------------------------------------------------------
# Test 4
# ---------------------------------------------------------------------
def test_linear_system_residual():
    alpha = default_alpha()
    N, P = 51, 0.8
    res = cda.run_uniform_array(N=N, period=P, alpha=alpha)
    A = cda.build_interaction_matrix(res["positions"], res["alphas"])
    residual = np.linalg.norm(A @ res["p_coupled"] - res["E_inc"]) / np.linalg.norm(res["E_inc"])
    report(
        "4. Linear system residual  ||A p − E_inc|| / ||E_inc||",
        residual < 1e-12,
        f"residual = {residual:.2e}  (N = {N}, P = {P} λ)",
    )


# ---------------------------------------------------------------------
# Test 5
# ---------------------------------------------------------------------
def test_mirror_symmetry():
    alpha = default_alpha()
    N, P = 21, 0.75
    res = cda.run_uniform_array(N=N, period=P, alpha=alpha)
    p = res["p_coupled"]
    positions = res["positions"]
    pos_err = float(np.max(np.abs(positions + positions[::-1])))
    amp_err = float(np.max(np.abs(np.abs(p) - np.abs(p[::-1]))))
    ph_err  = float(np.max(np.abs(np.angle(p) - np.angle(p[::-1]))))
    report(
        "5. Mirror symmetry of uniform centred array",
        pos_err < 1e-12 and amp_err < 1e-10 and ph_err < 1e-10,
        f"max |p_i − p_(N−1−i)|  amplitude = {amp_err:.2e},  phase = {ph_err:.2e} rad",
    )


# ---------------------------------------------------------------------
# Test 6
# ---------------------------------------------------------------------
def test_reciprocity_matrix():
    alpha = default_alpha()
    pos = cda.linear_array(11, 0.9)
    alphas = np.full(11, alpha, dtype=complex)
    A = cda.build_interaction_matrix(pos, alphas)
    mask = ~np.eye(11, dtype=bool)
    err = float(np.max(np.abs(A[mask] - A.T[mask])))
    report(
        "6. Matrix reciprocity  A_ij == A_ji",
        err < 1e-14,
        f"max off-diagonal asymmetry = {err:.2e}",
    )


# ---------------------------------------------------------------------
# Test 7
# ---------------------------------------------------------------------
def test_array_convergence():
    alpha = default_alpha()
    P = 0.8
    Ns = np.array([11, 21, 41, 81, 161, 321, 641])
    centre_dev = []
    for N in Ns:
        res = cda.run_uniform_array(N=int(N), period=P, alpha=alpha)
        idx = int(N) // 2
        dphi = cda.phase_deviation(res["p_coupled"], res["p_isolated"])
        centre_dev.append(np.degrees(dphi[idx]))
    centre_dev = np.array(centre_dev)
    diffs = np.abs(np.diff(centre_dev))
    final_diff = diffs[-1]
    valid = diffs > 0
    slope = float("nan")
    if valid.sum() >= 3:
        slope, _ = np.polyfit(np.log(Ns[1:][valid]), np.log(diffs[valid]), 1)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.2))
    ax1.semilogx(Ns, centre_dev, "o-", color="#1A478A")
    ax1.set_xlabel("array size N")
    ax1.set_ylabel("central atom Δφ  (deg)")
    ax1.set_title(f"Centre-atom phase deviation  (P = {P} λ)")
    ax1.grid(alpha=0.3)

    ax2.loglog(Ns[1:], diffs, "s-", color="#C0392B", label="|Δ between halvings|")
    ref = diffs[0] * np.sqrt(Ns[1] / Ns[1:])
    ax2.loglog(Ns[1:], ref, "k--", alpha=0.5, label="1/√N reference")
    ax2.set_xlabel("N")
    ax2.set_ylabel("|Δ|  (deg)")
    ax2.set_title(f"Convergence (fitted slope = {slope:.2f})")
    ax2.grid(alpha=0.3, which="both")
    ax2.legend()
    fig.tight_layout()
    out = os.path.join(FIG_DIR, "verification_convergence.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)

    ok = (-0.9 < slope < -0.2) and (final_diff < 0.5)
    report(
        "7. Array-size convergence (2D 1/√N lattice sum)",
        ok,
        f"values: {np.array2string(centre_dev, precision=3)}\n"
        f"        final |Δ| = {final_diff:.2e} deg, slope = {slope:.2f}  "
        f"(theory −0.5 for 2D)\n"
        f"        figure: {out}",
    )


# ---------------------------------------------------------------------
# Test 8
# ---------------------------------------------------------------------
def test_wavelength_scaling():
    alpha = default_alpha()
    pos1 = cda.linear_array(15, 0.8)
    alphas = np.full(15, alpha, dtype=complex)
    E_inc = cda.plane_wave_normal(pos1)
    p1 = cda.solve_cda(pos1, alphas, E_inc, k0=2 * np.pi)
    scale = 0.5
    p2 = cda.solve_cda(pos1 * scale, alphas, E_inc, k0=2 * np.pi / scale)
    err = float(np.max(np.abs(p1 - p2)) / np.max(np.abs(p1)))
    report(
        "8. Wavelength scaling invariance",
        err < 1e-12,
        f"max |p(k0) − p(k0/scale)| / max|p| = {err:.2e}  (scale = {scale})",
    )


# ---------------------------------------------------------------------
# Test 9
# ---------------------------------------------------------------------
def test_extinction_positive():
    alpha = default_alpha()
    periods = [0.5, 0.7, 1.2, 1.5, 2.5]
    Ns = [3, 21, 51]
    ok = True
    lines = []
    for N in Ns:
        for P in periods:
            res = cda.run_uniform_array(N=N, period=P, alpha=alpha)
            Pext = float(np.sum(np.imag(np.conj(res["E_inc"]) * res["p_coupled"])))
            lines.append(f"  N={N:>3}, P={P:>4.2f}   ->  P_ext = {Pext:+.4e}")
            if Pext <= 0:
                ok = False
    report(
        "9. Extinction power positivity (optical theorem inspired)",
        ok,
        "Im(E_inc* · p) > 0 for all configurations:\n        "
        + "\n        ".join(lines),
    )


# ---------------------------------------------------------------------
# Test 10
# ---------------------------------------------------------------------
def test_nonuniform_reduces_to_uniform():
    alpha = default_alpha()
    N, P = 15, 0.9
    pos = cda.linear_array(N, P)
    alphas = np.full(N, alpha, dtype=complex)
    ru = cda.run_uniform_array(N=N, period=P, alpha=alpha)
    rn = cda.run_nonuniform_array(positions=pos, alphas=alphas)
    err = float(np.max(np.abs(ru["p_coupled"] - rn["p_coupled"])))
    report(
        "10. Non-uniform solver reduces to uniform (identical α)",
        err < 1e-14,
        f"max |p_uniform − p_nonuniform| = {err:.2e}",
    )


# ---------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------
def summary():
    n_pass = sum(1 for tag, *_ in results if tag == PASS)
    n_fail = sum(1 for tag, *_ in results if tag == FAIL)
    total = len(results)
    print("=" * 70)
    print(f"VERIFICATION SUMMARY:  {n_pass} / {total} passed,  {n_fail} failed")
    print("=" * 70)
    for tag, name, _ in results:
        print(f"  [{tag}]  {name}")
    print()
    if n_fail == 0:
        print("All physical checks passed.")
    else:
        print("Some checks FAILED - please inspect.")


if __name__ == "__main__":
    print("=" * 70)
    print("CDA PHYSICAL VERIFICATION SUITE")
    print("=" * 70)
    print()
    test_single_dipole()
    test_two_dipole_analytical()
    test_green_function()
    test_linear_system_residual()
    test_mirror_symmetry()
    test_reciprocity_matrix()
    test_array_convergence()
    test_wavelength_scaling()
    test_extinction_positive()
    test_nonuniform_reduces_to_uniform()
    summary()
