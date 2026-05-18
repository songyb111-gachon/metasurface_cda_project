"""
Coupled Dipole Approximation (CDA) — 2D scalar implementation
for analyzing inter-meta-atom coupling in a 1D metasurface array.

Model
-----
Each meta-atom is a single point electric dipole with scalar
polarizability α(ω).  Dipoles sit on a 1D line with period P along the
x-axis.  Plane wave at normal incidence, E along the cylinder (z) axis
(TM scalar Helmholtz).  The free-space 2D scalar Green's function is

    G(r) = (i / 4) * H_0^{(1)}(k_0 r) ,

so that the self-consistent equations

    p_i = α_i ( E_inc,i + Σ_{j ≠ i} G(r_ij) p_j )

become the linear system

    A p = E_inc ,   A_ii = 1/α_i ,   A_ij = − G(|r_i − r_j|)  (i ≠ j).

We work in wavelength-normalized units (λ = 1, k_0 = 2π).
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np
from scipy.special import hankel1

K0 = 2.0 * np.pi
LAMBDA = 1.0


# ---------------------------------------------------------------------
# Polarizability model: damped Lorentzian
# ---------------------------------------------------------------------
@dataclass
class LorentzAlpha:
    """
    α(ω) = F / (ω₀² − ω² − i γ ω)

    Different meta-atom geometries are modelled by shifting ω₀.
    """

    omega0: float
    gamma: float = 0.2
    F: float = 1.0

    def __call__(self, omega: float = 2.0 * np.pi) -> complex:
        denom = self.omega0**2 - omega**2 - 1j * self.gamma * omega
        return self.F / denom


# ---------------------------------------------------------------------
# Green's function (2D scalar, free space)
# ---------------------------------------------------------------------
def greens_2d(r: np.ndarray, k0: float = K0) -> np.ndarray:
    """G(r) = (i/4) H_0^{(1)}(k_0 r) — vectorized over r."""
    r = np.asarray(r, dtype=float)
    return 0.25j * hankel1(0, k0 * r)


# ---------------------------------------------------------------------
# Geometry
# ---------------------------------------------------------------------
def linear_array(N: int, period: float, center: bool = True) -> np.ndarray:
    """Return x positions of N atoms with given period (centred if asked)."""
    x = np.arange(N, dtype=float) * period
    if center:
        x -= x.mean()
    return x


# ---------------------------------------------------------------------
# CDA core
# ---------------------------------------------------------------------
def build_interaction_matrix(
    positions: np.ndarray,
    alphas: np.ndarray,
    k0: float = K0,
) -> np.ndarray:
    """Assemble the N x N CDA matrix A."""
    positions = np.asarray(positions, dtype=float)
    alphas = np.asarray(alphas, dtype=complex)
    N = positions.size

    dx = positions[:, None] - positions[None, :]
    r = np.abs(dx)
    np.fill_diagonal(r, 1.0)            # placeholder; diagonal overwritten

    A = -greens_2d(r, k0=k0)
    np.fill_diagonal(A, 1.0 / alphas)
    return A


def solve_cda(
    positions: np.ndarray,
    alphas: np.ndarray,
    E_inc: np.ndarray,
    k0: float = K0,
) -> np.ndarray:
    """Solve A p = E_inc for the coupled dipole moments."""
    A = build_interaction_matrix(positions, alphas, k0=k0)
    return np.linalg.solve(A, E_inc)


def isolated_response(alphas: np.ndarray, E_inc: np.ndarray) -> np.ndarray:
    """p_iso = α · E_inc (no coupling)."""
    return np.asarray(alphas, dtype=complex) * np.asarray(E_inc, dtype=complex)


# ---------------------------------------------------------------------
# Incident field (normal-incidence plane wave, evaluated at y = 0)
# ---------------------------------------------------------------------
def plane_wave_normal(positions: np.ndarray, E0: complex = 1.0 + 0j) -> np.ndarray:
    return np.full(positions.shape, E0, dtype=complex)


# ---------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------
def phase_deviation(p_coupled: np.ndarray, p_isolated: np.ndarray) -> np.ndarray:
    """Per-dipole phase deviation Δφ_i = arg(p_coupled) − arg(p_iso), wrapped."""
    dphi = np.angle(p_coupled) - np.angle(p_isolated)
    return np.angle(np.exp(1j * dphi))


def mean_phase_deviation(p_coupled: np.ndarray, p_isolated: np.ndarray) -> float:
    return float(np.mean(np.abs(phase_deviation(p_coupled, p_isolated))))


def max_phase_deviation(p_coupled: np.ndarray, p_isolated: np.ndarray) -> float:
    return float(np.max(np.abs(phase_deviation(p_coupled, p_isolated))))


def amplitude_distortion_ratio(p_coupled: np.ndarray, p_isolated: np.ndarray) -> np.ndarray:
    return np.abs(p_coupled) / np.abs(p_isolated)


# ---------------------------------------------------------------------
# End-to-end helpers
# ---------------------------------------------------------------------
def run_uniform_array(
    N: int,
    period: float,
    alpha: complex,
    E0: complex = 1.0 + 0j,
    k0: float = K0,
) -> dict:
    positions = linear_array(N, period)
    alphas = np.full(N, alpha, dtype=complex)
    E_inc = plane_wave_normal(positions, E0=E0)

    p_coupled = solve_cda(positions, alphas, E_inc, k0=k0)
    p_iso = isolated_response(alphas, E_inc)

    return {
        "positions": positions,
        "alphas": alphas,
        "E_inc": E_inc,
        "p_coupled": p_coupled,
        "p_isolated": p_iso,
        "phase_dev": phase_deviation(p_coupled, p_iso),
        "mean_phase_dev": mean_phase_deviation(p_coupled, p_iso),
        "max_phase_dev": max_phase_deviation(p_coupled, p_iso),
    }


def run_nonuniform_array(
    positions: np.ndarray,
    alphas: np.ndarray,
    E0: complex = 1.0 + 0j,
    k0: float = K0,
) -> dict:
    positions = np.asarray(positions, dtype=float)
    alphas = np.asarray(alphas, dtype=complex)
    E_inc = plane_wave_normal(positions, E0=E0)

    p_coupled = solve_cda(positions, alphas, E_inc, k0=k0)
    p_iso = isolated_response(alphas, E_inc)

    return {
        "positions": positions,
        "alphas": alphas,
        "E_inc": E_inc,
        "p_coupled": p_coupled,
        "p_isolated": p_iso,
        "phase_dev": phase_deviation(p_coupled, p_iso),
        "mean_phase_dev": mean_phase_deviation(p_coupled, p_iso),
        "max_phase_dev": max_phase_deviation(p_coupled, p_iso),
    }
