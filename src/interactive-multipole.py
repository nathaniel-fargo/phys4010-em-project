"""
Interactive Multipole Superposition

Written for the PHYS 4010 E&M Final Project

Author: Nathaniel Fargo
Date: 12/2/2025

This project sets up a interactive way to configure multipole expansions up to the first 4 terms. One can view the individual terms, fields, and patterns, as well as seeing their final combination presented. 
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button

# Initial Conditions
DEFAULT_WEIGHTS = {
    "monopole": 1.0,
    "dipole": 0.6,
    "quadrupole": 0.4,
    "octupole": 0.3,
}

# A few variables that control the grid and slider ranges
GRID_POINTS = 260
R_MAX = 3.0
R_MIN = 0.1
SLIDER_MIN = -2.0
SLIDER_MAX = 2.0
# Mostly arbitray weight used to set color scale (smaller values brings out more color)
REFERENCE_COEFF = 0.0003


def legendre_poly(l_value, cos_theta):
    """Small helper with the only Legendre polynomials we need."""
    if l_value == 0:
        return np.ones_like(cos_theta)
    if l_value == 1:
        return cos_theta
    if l_value == 2:
        return 0.5 * (3 * cos_theta**2 - 1)
    if l_value == 3:
        return 0.5 * (5 * cos_theta**3 - 3 * cos_theta)
    raise ValueError("l must be between 0 and 3")


def multipole_term(l_value, coefficient, X, Y, R, mask):
    """Return the potential for a single multipole term."""
    if coefficient == 0:
        return np.zeros_like(R)

    cos_theta = np.zeros_like(Y)
    np.divide(Y, R, out=cos_theta, where=~mask)  # cos(theta)=z/r in this 2D slice
    P_l = legendre_poly(l_value, cos_theta)
    radial = np.power(R, -(l_value + 1), out=np.zeros_like(R), where=~mask)  # 1/r^(l+1)
    V = coefficient * P_l * radial
    V[mask] = np.nan
    return V


def plot_panel(ax, X, Y, V, title, vmax_override=None):
    """Draw a potential map on the given axis."""
    ax.cla()

    finite_vals = V[np.isfinite(V)]
    if vmax_override is not None:
        vmax = vmax_override
    elif finite_vals.size == 0:
        vmax = 1.0
    else:
        vmax = np.nanmax(np.abs(finite_vals))
        if vmax <= 1e-6:
            vmax = 1.0

    # Color map for potential (red = positive, blue = negative)
    mesh = ax.pcolormesh(
        X,
        Y,
        V,
        cmap="RdBu_r",
        shading="auto",
        vmin=-vmax,
        vmax=vmax,
    )

    if finite_vals.size > 0:
        levels = np.linspace(-vmax, vmax, 11)
        levels = levels[levels != 0]
        if levels.size > 0:
            ax.contour(
                X,
                Y,
                V,
                levels=levels,
                colors="white",
                linewidths=0.4,
                alpha=0.6,
            )  # white equipotential lines

    ax.add_patch(plt.Circle((0, 0), R_MIN, color="#151515", alpha=0.9))
    ax.set_aspect("equal")
    ax.set_facecolor("#050505")
    ax.set_title(title, fontsize=11)
    ax.set_xticks([])
    ax.set_yticks([])
    return mesh


def build_grid():
    """Set up the rectangular XY grid plus a mask that hides the origin."""
    x = np.linspace(-R_MAX, R_MAX, GRID_POINTS)
    y = np.linspace(-R_MAX, R_MAX, GRID_POINTS)
    X, Y = np.meshgrid(x, y)  # rectangular mesh for plotting
    R = np.sqrt(X**2 + Y**2)  # radial distance from origin
    mask = R < R_MIN  # skip a small circle near the origin
    return X, Y, R, mask


def build_figure():
    """Create the big total plot and the four small term panels."""
    plt.style.use("dark_background")
    fig = plt.figure(figsize=(14, 7.5), constrained_layout=False, facecolor="#050505")
    fig.suptitle(
        "Interactive Multipole Superposition",
        fontsize=16,
        color="#dddddd",
    )

    gridspec = fig.add_gridspec(
        2,
        3,
        left=0.05,
        right=0.95,
        bottom=0.18,
        top=0.86,
        width_ratios=[2.2, 1, 1],
        height_ratios=[1, 1],
        wspace=0.28,
        hspace=0.3,
    )

    ax_main = fig.add_subplot(gridspec[:, 0])
    ax_mono = fig.add_subplot(gridspec[0, 1])
    ax_dip = fig.add_subplot(gridspec[0, 2])
    ax_quad = fig.add_subplot(gridspec[1, 1])
    ax_oct = fig.add_subplot(gridspec[1, 2])

    return fig, ax_main, ax_mono, ax_dip, ax_quad, ax_oct


def create_sliders(fig, weights, on_change):
    """Create a 2x2 slider grid for each of the poles"""
    slider_width = 0.36
    slider_height = 0.035
    row_y = [0.09, 0.03]
    col_x = [0.08, 0.58]

    slider_axes = {
        "monopole": fig.add_axes([col_x[0], row_y[0], slider_width, slider_height], facecolor="#1b1b1b"),
        "dipole": fig.add_axes([col_x[1], row_y[0], slider_width, slider_height], facecolor="#1b1b1b"),
        "quadrupole": fig.add_axes([col_x[0], row_y[1], slider_width, slider_height], facecolor="#1b1b1b"),
        "octupole": fig.add_axes([col_x[1], row_y[1], slider_width, slider_height], facecolor="#1b1b1b"),
    }

    sliders = {
        "monopole": Slider(slider_axes["monopole"], "Monopole", SLIDER_MIN, SLIDER_MAX, valinit=weights["monopole"]),
        "dipole": Slider(slider_axes["dipole"], "Dipole", SLIDER_MIN, SLIDER_MAX, valinit=weights["dipole"]),
        "quadrupole": Slider(slider_axes["quadrupole"], "Quadrupole", SLIDER_MIN, SLIDER_MAX, valinit=weights["quadrupole"]),
        "octupole": Slider(slider_axes["octupole"], "Octupole", SLIDER_MIN, SLIDER_MAX, valinit=weights["octupole"]),
    }

    # Have sliders be red and blue to match polarity
    for _, slider in sliders.items():
        slider.poly.set_color("#f05050")  # fill along the bar
        slider.track.set_color("#50a0f0")
        slider.on_changed(on_change)
        slider.vline.set_visible(False)  # hide the red reference line

    return sliders


def compute_reference_vmax(X, Y, R, mask):
    """
    Pick a single color scale that keeps the plots comparable.

    We pretend every slider is set to REFERENCE_COEFF, find the largest
    magnitude we see, and reuse that number for every redraw.
    """
    candidate_max = 0.0
    total = np.zeros_like(R)
    for l_value in range(4):
        term = multipole_term(l_value, REFERENCE_COEFF, X, Y, R, mask)
        total += term
        valid = term[np.isfinite(term)]
        if valid.size:
            candidate_max = max(candidate_max, np.nanmax(np.abs(valid)))

    valid_total = total[np.isfinite(total)]
    if valid_total.size:
        candidate_max = max(candidate_max, np.nanmax(np.abs(valid_total)))

    if candidate_max <= 1e-6:
        candidate_max = 1.0
    return candidate_max


def compute_potentials(weights, X, Y, R, mask):
    """Calculate each term plus the total superposition."""
    term_info = [
        ("Monopole", 0, weights["monopole"]),
        ("Dipole", 1, weights["dipole"]),
        ("Quadrupole", 2, weights["quadrupole"]),
        ("Octupole", 3, weights["octupole"]),
    ]

    potentials = {}
    total = np.zeros_like(R)
    for label, l_value, coeff in term_info:
        V = multipole_term(l_value, coeff, X, Y, R, mask)
        potentials[label] = V
        total += V

    return potentials, total

weights = dict(DEFAULT_WEIGHTS)
X, Y, R, mask = build_grid()
shared_vmax = compute_reference_vmax(X, Y, R, mask)
fig, ax_main, ax_mono, ax_dip, ax_quad, ax_oct = build_figure()

def update_plots():
    """Redraw every axis using the current slider values."""
    potentials, total = compute_potentials(weights, X, Y, R, mask)

    plot_panel(ax_main, X, Y, total, "Total Potential", vmax_override=shared_vmax)
    plot_panel(ax_mono, X, Y, potentials["Monopole"], f"Monopole\nw = {weights['monopole']:.2f}", vmax_override=shared_vmax)
    plot_panel(ax_dip, X, Y, potentials["Dipole"], f"Dipole\nw = {weights['dipole']:.2f}", vmax_override=shared_vmax)
    plot_panel(ax_quad, X, Y, potentials["Quadrupole"], f"Quadrupole\nw = {weights['quadrupole']:.2f}", vmax_override=shared_vmax)
    plot_panel(ax_oct, X, Y, potentials["Octupole"], f"Octupole\nw = {weights['octupole']:.2f}", vmax_override=shared_vmax)

    fig.canvas.draw_idle()


sliders = {}


def on_slider_change(_=None):
    """Keep the weights dict in sync with the slider positions."""
    for key in weights:
        weights[key] = sliders[key].val
    update_plots()


sliders = create_sliders(fig, weights, on_slider_change)
update_plots()
plt.show()

