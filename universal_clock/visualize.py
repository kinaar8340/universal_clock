"""Egg of Life clock-face renderer."""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Wedge

from .clock import SLICES_PER_GEAR, UniversalPiClock

GEAR_COLORS = [
    "#e63946",  # Gear 1 — red
    "#f77f00",  # Gear 2 — orange
    "#fcbf49",  # Gear 3 — gold
    "#2a9d8f",  # Gear 4 — teal
    "#457b9d",  # Gear 5 — steel blue
    "#7b2cbf",  # Gear 6 — purple
    "#3a0ca3",  # Gear 7 — deep indigo
]

BG_COLOR = "#0d1117"
OUTLINE_COLOR = "#3d4f5f"
LABEL_COLOR = "#8b9cb3"
TEXT_COLOR = "#e6edf3"
DEFAULT_SLICE_LINES = 70


def egg_of_life_positions(
    radius: float = 1.0,
    *,
    first_gear_hour: float = 1.0,
) -> list[tuple[float, float]]:
    """Return (x, y) centers: index 0 = center gear, 1–6 = outer ring clockwise."""
    centers = [(0.0, 0.0)]
    # 12 o'clock in matplotlib = 90°; clockwise hour hand subtracts 30° per hour.
    start_deg = 90.0 - first_gear_hour * 30.0
    for i in range(6):
        angle_deg = start_deg - i * 60.0
        rad = math.radians(angle_deg)
        centers.append((radius * math.cos(rad), radius * math.sin(rad)))
    return centers


def _slice_angles(k: int) -> tuple[float, float]:
    """Wedge angles (degrees) for k filled slices starting at 12 o'clock, clockwise."""
    slice_deg = 360.0 / SLICES_PER_GEAR
    start = 90.0
    end = 90.0 - k * slice_deg
    return start, end


def draw_hand(
    ax: plt.Axes,
    center: tuple[float, float],
    radius: float,
    k: int,
    color: str,
    *,
    linewidth: float = 2.5,
) -> None:
    """Draw a thin hand pointing to the current k (1-based), clockwise from 12 o'clock."""
    if k < 1:
        k = 1
    angle_deg = 90.0 - ((k - 1) / SLICES_PER_GEAR) * 360.0
    angle_rad = np.deg2rad(angle_deg)

    hand_len = radius * 0.92
    cx, cy = center
    x_end = cx + hand_len * np.cos(angle_rad)
    y_end = cy + hand_len * np.sin(angle_rad)

    ax.plot(
        [cx, x_end],
        [cy, y_end],
        color=color,
        linewidth=linewidth,
        solid_capstyle="round",
        zorder=7,
    )
    ax.plot(x_end, y_end, "o", color=color, markersize=4, zorder=8)


def _draw_filled_slices(
    ax: plt.Axes,
    center: tuple[float, float],
    radius: float,
    k: int,
    color: str,
) -> None:
    if k <= 0:
        return
    start, end = _slice_angles(k)
    wedge = Wedge(
        center,
        radius,
        end,
        start,
        facecolor=color,
        edgecolor="none",
        alpha=0.82,
        zorder=2,
    )
    ax.add_patch(wedge)


def slice_line_step(num_lines: int = DEFAULT_SLICE_LINES) -> int:
    """Slices between radial lines (350 slices / 70 lines = every 5 slices)."""
    if num_lines <= 0 or SLICES_PER_GEAR % num_lines != 0:
        raise ValueError(
            f"slice_lines must divide {SLICES_PER_GEAR} evenly; got {num_lines}"
        )
    return SLICES_PER_GEAR // num_lines


def _draw_slice_ticks(
    ax: plt.Axes,
    center: tuple[float, float],
    radius: float,
    *,
    num_lines: int = DEFAULT_SLICE_LINES,
) -> None:
    """Radial slice lines around the circumference (default: 70 of 350 slices)."""
    cx, cy = center
    step = slice_line_step(num_lines)
    slice_rad = 2.0 * math.pi / SLICES_PER_GEAR
    lw = 0.28 if num_lines >= 70 else 0.35
    alpha = 0.38 if num_lines >= 70 else 0.45
    for i in range(0, SLICES_PER_GEAR, step):
        # 12 o'clock clockwise
        theta = math.pi / 2.0 - i * slice_rad
        inner = radius * 0.96
        ax.plot(
            [cx + inner * math.cos(theta), cx + radius * math.cos(theta)],
            [cy + inner * math.sin(theta), cy + radius * math.sin(theta)],
            color=OUTLINE_COLOR,
            lw=lw,
            alpha=alpha,
            zorder=3,
        )


def _draw_slice_labels(
    ax: plt.Axes,
    center: tuple[float, float],
    radius: float,
    *,
    every: int = 50,
) -> None:
    """Place k/π labels at selected slice positions around the circumference."""
    cx, cy = center
    slice_rad = 2.0 * math.pi / SLICES_PER_GEAR
    label_r = radius * 1.08
    for k in range(1, SLICES_PER_GEAR + 1, every):
        theta = math.pi / 2.0 - (k - 0.5) * slice_rad
        ax.text(
            cx + label_r * math.cos(theta),
            cy + label_r * math.sin(theta),
            f"{k}/π",
            ha="center",
            va="center",
            fontsize=4.5,
            color=LABEL_COLOR,
            alpha=0.75,
            zorder=4,
        )


def _draw_gear_circle(
    ax: plt.Axes,
    center: tuple[float, float],
    radius: float,
    gear_num: int,
    k: int,
    color: str,
    *,
    show_ticks: bool = True,
    show_labels: bool = True,
    show_hands: bool = True,
    label_every: int = 50,
    slice_lines: int = DEFAULT_SLICE_LINES,
) -> None:
    cx, cy = center
    _draw_filled_slices(ax, (cx, cy), radius, k, color)
    if show_hands:
        draw_hand(ax, (cx, cy), radius, k, color)
    outline = Circle(
        (cx, cy),
        radius,
        fill=False,
        edgecolor=OUTLINE_COLOR,
        lw=1.4,
        zorder=5,
    )
    ax.add_patch(outline)
    if show_ticks:
        _draw_slice_ticks(ax, (cx, cy), radius, num_lines=slice_lines)
    if show_labels:
        _draw_slice_labels(ax, (cx, cy), radius, every=label_every)
    v = k / math.pi
    ax.text(
        cx,
        cy,
        f"G{gear_num}\nk={k}\nv≈{v:.2f}",
        ha="center",
        va="center",
        fontsize=7 if gear_num == 1 else 6,
        color=TEXT_COLOR,
        fontweight="bold" if gear_num == 1 else "normal",
        zorder=6,
    )


def draw_clock(
    ax: plt.Axes,
    clock: UniversalPiClock,
    *,
    circle_radius: float = 1.0,
    show_ticks: bool = True,
    show_labels: bool = True,
    show_hands: bool = True,
    slice_lines: int = DEFAULT_SLICE_LINES,
    title: str | None = None,
) -> None:
    """Draw the Egg of Life clock face onto an existing axes."""
    centers = egg_of_life_positions(circle_radius)
    span = circle_radius * 3.6

    ax.clear()
    ax.set_facecolor(BG_COLOR)
    ax.set_aspect("equal")
    ax.set_xlim(-span, span)
    ax.set_ylim(-span, span)
    ax.axis("off")

    for gear_num in range(1, 8):
        idx = gear_num - 1
        _draw_gear_circle(
            ax,
            centers[idx],
            circle_radius,
            gear_num,
            clock.gears[idx],
            GEAR_COLORS[idx],
            show_ticks=show_ticks,
            show_labels=show_labels,
            show_hands=show_hands,
            slice_lines=slice_lines,
        )

    if title is None:
        title = (
            f"Universal π Clock · Egg of Life\n"
            f"{clock.total_ticks:,} ticks · "
            + " · ".join(f"G{i}={clock.gears[i-1]}" for i in range(1, 8))
        )
    ax.set_title(title, color=TEXT_COLOR, fontsize=11, pad=16)


def render_clock(
    clock: UniversalPiClock,
    *,
    output: Path | str | None = None,
    dpi: int = 200,
    figsize: tuple[float, float] = (12, 12),
    circle_radius: float = 1.0,
    show_ticks: bool = True,
    show_labels: bool = True,
    show_hands: bool = True,
    slice_lines: int = DEFAULT_SLICE_LINES,
    title: str | None = None,
) -> plt.Figure:
    """Render the Egg of Life clock face for the current clock state."""
    fig, ax = plt.subplots(figsize=figsize, facecolor=BG_COLOR)
    draw_clock(
        ax,
        clock,
        circle_radius=circle_radius,
        show_ticks=show_ticks,
        show_labels=show_labels,
        show_hands=show_hands,
        slice_lines=slice_lines,
        title=title,
    )
    fig.tight_layout()
    if output is not None:
        fig.savefig(output, dpi=dpi, facecolor=BG_COLOR, bbox_inches="tight")
    return fig