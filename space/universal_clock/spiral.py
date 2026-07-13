"""Golden / logarithmic spiral clock-face renderer.

Primary visual metaphor: time spiraling outward along a golden spiral
  r = a · exp(b · θ),  b = ln(φ) / (π/2),  φ = (1+√5)/2

Styles
------
golden_spiral
    Portrait card (THEMATHFLOW-inspired). Gear 1 drives the spiral hand;
    gears 2–7 appear as color-coded markers on outer turns + vertical stacks.

spiral_arms
    Seven successive spiral arms expanding outward (one per gear).

hybrid
    Egg of Life nest at the center; a golden spiral grows outward for G1+
    with faint higher-gear arm indicators.
"""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Wedge

from .clock import NUM_GEARS, SLICES_PER_GEAR, UniversalPiClock

# Shared palette / helpers live in visualize; imported lazily where needed
# to avoid circular imports (visualize dispatches into this module).

# ── Golden spiral constants ──────────────────────────────────────────────────

PHI = (1.0 + math.sqrt(5.0)) / 2.0
B_GOLDEN = math.log(PHI) / (math.pi / 2.0)  # ≈ 0.306349

# Full Gear-1 revolution maps to this many spiral turns.
DEFAULT_SPIRAL_TURNS = 2.0

# Light (video-card) palette
LIGHT_BG = "#f7f4ef"
LIGHT_CARD = "#faf8f4"
LIGHT_INK = "#2c2c2c"
LIGHT_MUTED = "#9a9590"
LIGHT_ACCENT = "#e63946"
LIGHT_FACE = "#e8e4de"
LIGHT_TICK = "#6b6560"
LIGHT_SPIRAL = "#1a1a1a"

# Dark palette (mirrors visualize defaults — keep in sync)
BG_COLOR = "#0d1117"
OUTLINE_COLOR = "#3d4f5f"
LABEL_COLOR = "#8b9cb3"
TEXT_COLOR = "#e6edf3"
DARK_SPIRAL = "#c9d1d9"
GEAR_COLORS = [
    "#e63946",
    "#f77f00",
    "#fcbf49",
    "#2a9d8f",
    "#457b9d",
    "#7b2cbf",
    "#3a0ca3",
]
DEFAULT_SLICE_LINES = 70

VISUAL_STYLES = ("egg_of_life", "golden_spiral", "spiral_arms", "hybrid")
LAYOUTS = ("portrait", "landscape", "square")


def _slice_line_step(num_lines: int = DEFAULT_SLICE_LINES) -> int:
    if num_lines <= 0 or SLICES_PER_GEAR % num_lines != 0:
        raise ValueError(
            f"slice_lines must divide {SLICES_PER_GEAR} evenly; got {num_lines}"
        )
    return SLICES_PER_GEAR // num_lines


def theta_for_slice(
    k: int,
    *,
    slices: int = SLICES_PER_GEAR,
    turns: float = DEFAULT_SPIRAL_TURNS,
) -> float:
    """Map 1-based slice index k to spiral angle θ ∈ [0, turns·2π]."""
    k = max(1, min(int(k), slices))
    frac = (k - 1) / max(slices - 1, 1)
    return frac * turns * 2.0 * math.pi


def spiral_radius(theta: float | np.ndarray, a: float = 1.0) -> float | np.ndarray:
    """r(θ) = a · exp(b · θ) with golden growth rate b."""
    return a * np.exp(B_GOLDEN * np.asarray(theta, dtype=float))


def spiral_xy(
    theta: float | np.ndarray,
    a: float = 1.0,
    *,
    start_angle: float = math.pi / 2.0,
    clockwise: bool = True,
) -> tuple[np.ndarray, np.ndarray]:
    """Cartesian points on the golden spiral.

    θ = 0 starts at ``start_angle`` (default: 12 o'clock). Positive θ advances
    clockwise when ``clockwise`` is True (standard clock convention).
    """
    th = np.asarray(theta, dtype=float)
    r = spiral_radius(th, a)
    ang = start_angle - th if clockwise else start_angle + th
    return r * np.cos(ang), r * np.sin(ang)


def spiral_curve(
    theta_end: float,
    a: float = 1.0,
    *,
    n_points: int = 400,
    start_angle: float = math.pi / 2.0,
    clockwise: bool = True,
) -> tuple[np.ndarray, np.ndarray]:
    """Dense polyline from θ=0 to θ=theta_end."""
    if theta_end <= 0:
        x, y = spiral_xy(0.0, a, start_angle=start_angle, clockwise=clockwise)
        return np.atleast_1d(x), np.atleast_1d(y)
    thetas = np.linspace(0.0, theta_end, max(n_points, 2))
    return spiral_xy(thetas, a, start_angle=start_angle, clockwise=clockwise)


def spiral_tangent_angle(
    theta: float,
    *,
    start_angle: float = math.pi / 2.0,
    clockwise: bool = True,
) -> float:
    """Angle (radians) of the outward tangent at θ — useful for tick marks."""
    # Polar: r = a e^{bθ}, clockwise mapping ang = start − θ
    # dr/dθ = b r; tangential direction in (x,y) is approx ang ± atan(1/b) offset
    # Simpler: direction of increasing θ on the curve.
    sign = -1.0 if clockwise else 1.0
    ang = start_angle + sign * theta
    # Velocity angle for log spiral: radial component + azimuthal
    # φ_tangent = ang + atan2(sign, B_GOLDEN)  (approx)
    return ang + math.atan2(sign, B_GOLDEN)


# ── Shared helpers ───────────────────────────────────────────────────────────

def _palette(theme: str) -> dict[str, str]:
    if theme == "light":
        return {
            "bg": LIGHT_BG,
            "card": LIGHT_CARD,
            "ink": LIGHT_INK,
            "muted": LIGHT_MUTED,
            "accent": LIGHT_ACCENT,
            "face": LIGHT_FACE,
            "tick": LIGHT_TICK,
            "spiral": LIGHT_SPIRAL,
            "outline": "#c4bfb8",
            "text": LIGHT_INK,
            "label": LIGHT_MUTED,
        }
    return {
        "bg": BG_COLOR,
        "card": BG_COLOR,
        "ink": TEXT_COLOR,
        "muted": LABEL_COLOR,
        "accent": GEAR_COLORS[0],
        "face": "#161b22",
        "tick": OUTLINE_COLOR,
        "spiral": DARK_SPIRAL,
        "outline": OUTLINE_COLOR,
        "text": TEXT_COLOR,
        "label": LABEL_COLOR,
    }


def _figsize_for_layout(layout: str, base: float = 10.0) -> tuple[float, float]:
    if layout == "portrait":
        return (base * 0.62, base * 1.05)
    if layout == "landscape":
        return (base * 1.2, base * 0.72)
    return (base, base)


def _draw_center_dial(
    ax: plt.Axes,
    center: tuple[float, float],
    radius: float,
    k: int,
    color: str,
    pal: dict[str, str],
    *,
    show_ticks: bool = True,
    show_hands: bool = True,
    slice_lines: int = DEFAULT_SLICE_LINES,
    fill_alpha: float = 0.55,
) -> None:
    """Compact circular dial for Gear 1 at spiral origin."""
    cx, cy = center
    face = Circle(
        (cx, cy),
        radius,
        facecolor=pal["face"],
        edgecolor=pal["outline"],
        lw=1.6,
        zorder=3,
    )
    ax.add_patch(face)

    if k > 0:
        slice_deg = 360.0 / SLICES_PER_GEAR
        start = 90.0
        end = 90.0 - k * slice_deg
        wedge = Wedge(
            (cx, cy),
            radius * 0.96,
            end,
            start,
            facecolor=color,
            edgecolor="none",
            alpha=fill_alpha,
            zorder=4,
        )
        ax.add_patch(wedge)

    if show_ticks:
        step = _slice_line_step(slice_lines)
        slice_rad = 2.0 * math.pi / SLICES_PER_GEAR
        for i in range(0, SLICES_PER_GEAR, step):
            theta = math.pi / 2.0 - i * slice_rad
            major = i % (step * 5) == 0
            inner = radius * (0.82 if major else 0.90)
            outer = radius * 0.98
            ax.plot(
                [cx + inner * math.cos(theta), cx + outer * math.cos(theta)],
                [cy + inner * math.sin(theta), cy + outer * math.sin(theta)],
                color=pal["tick"],
                lw=0.9 if major else 0.35,
                alpha=0.85 if major else 0.45,
                zorder=5,
            )

    hub = Circle((cx, cy), radius * 0.08, facecolor=color, edgecolor="none", zorder=9)
    ax.add_patch(hub)

    if show_hands:
        from .visualize import draw_hand

        draw_hand(ax, (cx, cy), radius, k, color, linewidth=2.0)


def _draw_spiral_hand(
    ax: plt.Axes,
    a: float,
    k: int,
    color: str,
    *,
    turns: float = DEFAULT_SPIRAL_TURNS,
    linewidth: float = 2.4,
    alpha: float = 1.0,
    zorder: int = 6,
    tip_size: float = 6.0,
    n_points: int = 500,
) -> tuple[float, float]:
    """Draw spiral from center to slice k; return tip (x, y)."""
    th = theta_for_slice(k, turns=turns)
    xs, ys = spiral_curve(th, a, n_points=n_points)
    ax.plot(
        xs,
        ys,
        color=color,
        lw=linewidth,
        alpha=alpha,
        solid_capstyle="round",
        zorder=zorder,
    )
    tip_x, tip_y = float(xs[-1]), float(ys[-1])
    if tip_size > 0:
        ax.plot(
            tip_x,
            tip_y,
            "o",
            color=color,
            markersize=tip_size,
            zorder=zorder + 1,
        )
    return tip_x, tip_y


def _draw_full_spiral_guide(
    ax: plt.Axes,
    a: float,
    pal: dict[str, str],
    *,
    turns: float = DEFAULT_SPIRAL_TURNS,
    alpha: float = 0.18,
    linewidth: float = 1.0,
    n_points: int = 600,
) -> None:
    """Faint full-revolution spiral track."""
    th_end = turns * 2.0 * math.pi
    xs, ys = spiral_curve(th_end, a, n_points=n_points)
    ax.plot(
        xs,
        ys,
        color=pal["spiral"],
        lw=linewidth,
        alpha=alpha,
        solid_capstyle="round",
        zorder=2,
    )


def _draw_slice_ticks_on_spiral(
    ax: plt.Axes,
    a: float,
    pal: dict[str, str],
    *,
    turns: float = DEFAULT_SPIRAL_TURNS,
    num_lines: int = DEFAULT_SLICE_LINES,
    tick_len: float = 0.06,
) -> None:
    """Short ticks normal to the spiral at every N slices."""
    step = _slice_line_step(num_lines)
    for i in range(0, SLICES_PER_GEAR, step):
        k = i + 1
        th = theta_for_slice(k, turns=turns)
        x, y = spiral_xy(th, a)
        x, y = float(x), float(y)
        # Radial tick (toward/away from origin) — readable and cheap
        r = math.hypot(x, y)
        if r < 1e-9:
            continue
        ux, uy = x / r, y / r
        major = i % (step * 5) == 0
        length = tick_len * (1.6 if major else 1.0)
        ax.plot(
            [x - ux * length * 0.3, x + ux * length],
            [y - uy * length * 0.3, y + uy * length],
            color=pal["tick"],
            lw=0.8 if major else 0.35,
            alpha=0.7 if major else 0.4,
            zorder=3,
        )


def _draw_k_pi_labels_on_spiral(
    ax: plt.Axes,
    a: float,
    pal: dict[str, str],
    *,
    turns: float = DEFAULT_SPIRAL_TURNS,
    every: int = 50,
) -> None:
    for k in range(1, SLICES_PER_GEAR + 1, every):
        th = theta_for_slice(k, turns=turns)
        x, y = spiral_xy(th, a)
        x, y = float(x), float(y)
        r = math.hypot(x, y)
        if r < 1e-9:
            continue
        # Offset outward along radial direction
        scale = 1.0 + 0.12 * a / max(r, 0.01)
        ax.text(
            x * scale,
            y * scale,
            f"{k}/π",
            ha="center",
            va="center",
            fontsize=5,
            color=pal["label"],
            alpha=0.8,
            zorder=4,
        )


def _draw_coarser_gear_markers(
    ax: plt.Axes,
    clock: UniversalPiClock,
    a: float,
    *,
    turns: float = DEFAULT_SPIRAL_TURNS,
    dial_radius: float = 0.55,
    max_r: float = 1.85,
) -> None:
    """Place G2–G7 as colored dots along successive outer spiral bands.

    Each gear owns a φ-scaled arm. Even at k=1 the marker sits on a distinct
    radius so labels do not collapse onto the origin. Positions are clamped
    inside ``max_r`` so portrait frames do not clip labels.
    """
    for gear_num in range(2, NUM_GEARS + 1):
        k = clock.gears[gear_num - 1]
        # Moderate φ growth — stay inside portrait bounds
        a_g = a * (PHI ** (0.38 * (gear_num - 1)))
        # Spread gears around the spiral: base angle from gear index + k progress
        base_th = (gear_num - 2) / max(NUM_GEARS - 2, 1) * (turns * 0.45 * 2 * math.pi)
        th = base_th + theta_for_slice(k, turns=turns * 0.30)
        x, y = spiral_xy(th, a_g)
        x, y = float(x), float(y)
        # Keep markers outside the dial face and inside the card
        r = math.hypot(x, y)
        min_r = dial_radius * 1.18
        if r < 1e-9:
            ang = math.pi / 2.0 - (gear_num - 2) * (2 * math.pi / 6)
            x = min_r * math.cos(ang)
            y = min_r * math.sin(ang)
            r = min_r
        else:
            if r < min_r:
                scale = min_r / r
                x, y = x * scale, y * scale
                r = min_r
            if r > max_r:
                scale = max_r / r
                x, y = x * scale, y * scale
                r = max_r
        color = GEAR_COLORS[gear_num - 1]
        ax.plot(
            x,
            y,
            "o",
            color=color,
            markersize=max(3.5, 7.5 - gear_num * 0.4),
            markeredgecolor="white",
            markeredgewidth=0.55,
            zorder=8,
            alpha=0.92,
        )
        # Label offset outward (also clamped)
        if r > 1e-6:
            ox, oy = x / r * 0.16, y / r * 0.16
        else:
            ox, oy = 0.0, 0.16
        lx, ly = x + ox, y + oy
        lim = max_r * 1.05
        mag = math.hypot(lx, ly)
        if mag > lim and mag > 1e-9:
            lx, ly = lx / mag * lim, ly / mag * lim
        ax.text(
            lx,
            ly,
            f"G{gear_num}",
            fontsize=5.5,
            color=color,
            ha="center",
            va="center",
            zorder=9,
            fontweight="bold",
        )


def _draw_vertical_gear_stacks(
    ax: plt.Axes,
    clock: UniversalPiClock,
    pal: dict[str, str],
    *,
    x: float = 0.0,
    y_top: float = 2.55,
    y_bottom: float = -2.55,
    spacing: float = 0.32,
) -> None:
    """THEMATHFLOW-style vertical number stacks for gear values.

    Upper stack: G4–G7 (slow → top). Lower stack: G1–G3 (fast near dial).
    Active-looking: largest k among stack gets accent underline (visual cue).
    """
    # Upper: G7 at top … G4 near dial
    upper = list(range(7, 3, -1))  # 7,6,5,4
    for i, g in enumerate(upper):
        yy = y_top - i * spacing
        k = clock.gears[g - 1]
        color = GEAR_COLORS[g - 1]
        # Arc-like tick bar
        ax.plot(
            [x - 0.22, x + 0.22],
            [yy, yy],
            color=color,
            lw=2.0,
            solid_capstyle="round",
            alpha=0.85,
            zorder=5,
        )
        ax.text(
            x + 0.38,
            yy,
            f"G{g}  {k}/π",
            ha="left",
            va="center",
            fontsize=7.5,
            color=pal["ink"],
            zorder=6,
            fontfamily="sans-serif",
        )

    # Lower: G3 … G1 then (implicit dial), then show G? wait
    # Video has 7-12 below; we map G3,G2,G1 near dial and show total ticks at bottom.
    lower = [3, 2, 1]
    for i, g in enumerate(lower):
        yy = -0.95 - i * spacing  # below dial
        k = clock.gears[g - 1]
        color = GEAR_COLORS[g - 1]
        ax.plot(
            [x - 0.22, x + 0.22],
            [yy, yy],
            color=color,
            lw=2.4 if g == 1 else 2.0,
            solid_capstyle="round",
            alpha=0.95 if g == 1 else 0.85,
            zorder=5,
        )
        label = f"G{g}  {k}/π"
        ax.text(
            x + 0.38,
            yy,
            label,
            ha="left",
            va="center",
            fontsize=8 if g == 1 else 7.5,
            color=pal["accent"] if g == 1 else pal["ink"],
            fontweight="bold" if g == 1 else "normal",
            zorder=6,
        )


def _draw_portrait_card_chrome(
    ax: plt.Axes,
    pal: dict[str, str],
    clock: UniversalPiClock,
    *,
    title: str | None,
) -> None:
    """Brand strip + digital readout for portrait card layout."""
    brand = "UNIVERSAL π CLOCK"
    ax.text(
        0.0,
        3.05,
        brand,
        ha="center",
        va="center",
        fontsize=8,
        color=pal["muted"],
        zorder=10,
        fontweight="normal",
    )
    ax.text(
        0.0,
        -3.05,
        f"{clock.total_ticks:,} ticks",
        ha="center",
        va="center",
        fontsize=11,
        color=pal["accent"],
        fontweight="bold",
        zorder=10,
    )
    ax.text(
        0.0,
        -3.35,
        " · ".join(f"G{i}={clock.gears[i - 1]}" for i in range(1, 8)),
        ha="center",
        va="center",
        fontsize=6.5,
        color=pal["muted"],
        zorder=10,
    )
    if title:
        ax.set_title(title, color=pal["text"], fontsize=10, pad=8)


# ── Public drawing entry points ──────────────────────────────────────────────

def draw_golden_spiral_clock(
    ax: plt.Axes,
    clock: UniversalPiClock,
    *,
    theme: str = "dark",
    layout: str = "portrait",
    spiral_a: float = 0.14,
    turns: float = DEFAULT_SPIRAL_TURNS,
    show_ticks: bool = True,
    show_labels: bool = True,
    show_hands: bool = True,
    slice_lines: int = DEFAULT_SLICE_LINES,
    title: str | None = None,
    dial_radius: float = 0.55,
) -> None:
    """Portrait/landscape golden-spiral face: G1 spiral + coarser overlays."""
    pal = _palette(theme)
    ax.clear()
    ax.set_facecolor(pal["bg"])
    ax.set_aspect("equal")
    ax.axis("off")

    if layout == "portrait":
        ax.set_xlim(-2.0, 2.6)
        ax.set_ylim(-3.6, 3.3)
    elif layout == "landscape":
        ax.set_xlim(-3.4, 3.4)
        ax.set_ylim(-2.0, 2.2)
    else:
        ax.set_xlim(-2.8, 2.8)
        ax.set_ylim(-2.8, 2.8)

    # Full spiral guide track
    _draw_full_spiral_guide(ax, spiral_a, pal, turns=turns, alpha=0.22, linewidth=1.2)

    if show_ticks:
        _draw_slice_ticks_on_spiral(
            ax, spiral_a, pal, turns=turns, num_lines=slice_lines
        )
    if show_labels:
        _draw_k_pi_labels_on_spiral(ax, spiral_a, pal, turns=turns)

    # Active G1 spiral hand
    g1_color = GEAR_COLORS[0]
    _draw_spiral_hand(
        ax,
        spiral_a,
        clock.gears[0],
        g1_color if theme == "dark" else LIGHT_SPIRAL,
        turns=turns,
        linewidth=2.6,
        tip_size=5.5,
    )

    # Coarser gear markers on φ-scaled arms
    _draw_coarser_gear_markers(
        ax, clock, spiral_a, turns=turns, dial_radius=dial_radius
    )

    # Center dial (G1)
    _draw_center_dial(
        ax,
        (0.0, 0.0),
        dial_radius,
        clock.gears[0],
        g1_color,
        pal,
        show_ticks=show_ticks,
        show_hands=show_hands,
        slice_lines=min(slice_lines, 70),
    )

    # Center value text (below hub so hand remains readable)
    k1 = clock.gears[0]
    ax.text(
        0.0,
        -dial_radius * 0.28,
        f"G1  {k1}/π",
        ha="center",
        va="center",
        fontsize=6.5,
        color=pal["text"],
        fontweight="bold",
        zorder=10,
    )

    if layout == "portrait":
        _draw_vertical_gear_stacks(ax, clock, pal)
        if title is None:
            title = ""
        _draw_portrait_card_chrome(ax, pal, clock, title=title or None)
    else:
        # Compact legend for non-portrait
        for i in range(NUM_GEARS):
            ax.text(
                -2.5 if layout == "square" else -3.1,
                2.4 - i * 0.28,
                f"G{i + 1}={clock.gears[i]}  v≈{clock.values[i]:.2f}",
                fontsize=7,
                color=GEAR_COLORS[i],
                ha="left",
                va="center",
                zorder=10,
            )
        if title is None:
            title = (
                f"Universal π Clock · Golden Spiral\n"
                f"{clock.total_ticks:,} ticks"
            )
        if title:
            ax.set_title(title, color=pal["text"], fontsize=11, pad=12)


def draw_spiral_arms_clock(
    ax: plt.Axes,
    clock: UniversalPiClock,
    *,
    theme: str = "dark",
    turns: float = 1.6,
    base_a: float = 0.22,
    show_ticks: bool = True,
    show_labels: bool = False,
    show_hands: bool = True,
    slice_lines: int = DEFAULT_SLICE_LINES,
    title: str | None = None,
) -> None:
    """Each gear is its own expanding spiral arm (φ-scaled)."""
    pal = _palette(theme)
    ax.clear()
    ax.set_facecolor(pal["bg"])
    ax.set_aspect("equal")
    ax.axis("off")

    # Fixed readable span (not dominated by unused outer arm extent)
    span = 3.4
    ax.set_xlim(-span, span)
    ax.set_ylim(-span, span)

    for gear_num in range(1, NUM_GEARS + 1):
        idx = gear_num - 1
        # Moderate φ growth so all seven arms stay in frame
        a = base_a * (PHI ** (0.42 * idx))
        color = GEAR_COLORS[idx]
        k = clock.gears[idx]
        arm_turns = turns * (1.0 - 0.06 * idx)
        # Faint full track
        _draw_full_spiral_guide(
            ax,
            a,
            {"spiral": color},
            turns=arm_turns,
            alpha=0.20,
            linewidth=1.1,
            n_points=400,
        )
        # Active spiral hand for this gear's true k
        _draw_spiral_hand(
            ax,
            a,
            k,
            color,
            turns=arm_turns,
            linewidth=2.6 if gear_num == 1 else 1.8,
            alpha=0.95 if gear_num == 1 else 0.72,
            tip_size=6.0 if gear_num == 1 else 4.0,
            n_points=450,
            zorder=4 + gear_num,
        )
        if show_labels and gear_num == 1:
            _draw_k_pi_labels_on_spiral(
                ax, a, pal, turns=arm_turns, every=70
            )

    # Hub
    hub_r = 0.18
    ax.add_patch(
        Circle(
            (0.0, 0.0),
            hub_r,
            facecolor=pal["face"] if theme == "light" else "#161b22",
            edgecolor=pal["outline"],
            lw=1.2,
            zorder=12,
        )
    )
    ax.plot(0, 0, "o", color=GEAR_COLORS[0], markersize=5, zorder=13)

    # Legend
    for i in range(NUM_GEARS):
        ax.text(
            -span * 0.95,
            span * 0.92 - i * 0.28,
            f"G{i + 1}  k={clock.gears[i]}  v≈{clock.values[i]:.2f}",
            fontsize=8,
            color=GEAR_COLORS[i],
            ha="left",
            va="center",
            zorder=15,
            fontweight="bold" if i == 0 else "normal",
        )

    if title is None:
        title = (
            f"Universal π Clock · Spiral Arms\n"
            f"{clock.total_ticks:,} ticks"
        )
    if title:
        ax.set_title(title, color=pal["text"], fontsize=11, pad=12)


def draw_hybrid_clock(
    ax: plt.Axes,
    clock: UniversalPiClock,
    *,
    theme: str = "dark",
    circle_radius: float = 0.85,
    spiral_a: float = 0.22,
    turns: float = DEFAULT_SPIRAL_TURNS,
    show_ticks: bool = True,
    show_labels: bool = True,
    show_hands: bool = True,
    slice_lines: int = DEFAULT_SLICE_LINES,
    title: str | None = None,
    growth: float = 1.0,
) -> None:
    """Egg of Life center + golden spiral growing outward.

    ``growth`` ∈ [0.5, 1.5] scales spiral extent (carry-over animation hook).
    """
    from .visualize import draw_hand, egg_of_life_positions

    pal = _palette(theme)
    ax.clear()
    ax.set_facecolor(pal["bg"])
    ax.set_aspect("equal")
    ax.axis("off")

    centers = egg_of_life_positions(circle_radius)
    growth = max(0.4, min(float(growth), 2.0))
    # Keep spiral comparable to Egg of Life footprint
    a = spiral_a * growth * 0.55
    hybrid_turns = turns * 0.85
    outer = float(spiral_radius(hybrid_turns * 2.0 * math.pi, a)) * 1.08
    span = max(circle_radius * 3.55, outer * 1.05)
    ax.set_xlim(-span, span)
    ax.set_ylim(-span, span)

    # Outer spiral layers first (behind Egg of Life)
    _draw_full_spiral_guide(
        ax, a, pal, turns=hybrid_turns, alpha=0.28, linewidth=1.3
    )
    _draw_spiral_hand(
        ax,
        a,
        clock.gears[0],
        GEAR_COLORS[0],
        turns=hybrid_turns,
        linewidth=2.4,
        alpha=0.92,
        tip_size=5.5,
        zorder=2,
    )
    # Higher gears as faint outer arms (capped scale so egg stays dominant)
    for gear_num in range(2, min(NUM_GEARS, 4) + 1):
        a_g = a * (PHI ** (0.28 * (gear_num - 1)))
        k_g = clock.gears[gear_num - 1]
        _draw_spiral_hand(
            ax,
            a_g,
            max(k_g, 1),
            GEAR_COLORS[gear_num - 1],
            turns=hybrid_turns * 0.7,
            linewidth=1.3,
            alpha=0.40,
            tip_size=3.0,
            zorder=2,
            n_points=300,
        )

    # Egg of Life gears (compact, slightly transparent outlines)
    for gear_num in range(1, 8):
        idx = gear_num - 1
        cx, cy = centers[idx]
        color = GEAR_COLORS[idx]
        k = clock.gears[idx]
        r = circle_radius * (0.92 if gear_num == 1 else 0.88)

        if k > 0:
            slice_deg = 360.0 / SLICES_PER_GEAR
            start, end = 90.0, 90.0 - k * slice_deg
            ax.add_patch(
                Wedge(
                    (cx, cy),
                    r,
                    end,
                    start,
                    facecolor=color,
                    edgecolor="none",
                    alpha=0.72,
                    zorder=5,
                )
            )
        ax.add_patch(
            Circle(
                (cx, cy),
                r,
                fill=False,
                edgecolor=pal["outline"],
                lw=1.2,
                zorder=6,
            )
        )
        if show_hands:
            draw_hand(ax, (cx, cy), r, k, color, linewidth=1.8)
        if show_ticks and gear_num == 1:
            step = _slice_line_step(min(slice_lines, 70))
            slice_rad = 2.0 * math.pi / SLICES_PER_GEAR
            for i in range(0, SLICES_PER_GEAR, step):
                theta = math.pi / 2.0 - i * slice_rad
                inner = r * 0.94
                ax.plot(
                    [cx + inner * math.cos(theta), cx + r * math.cos(theta)],
                    [cy + inner * math.sin(theta), cy + r * math.sin(theta)],
                    color=pal["outline"],
                    lw=0.3,
                    alpha=0.4,
                    zorder=6,
                )
        ax.text(
            cx,
            cy,
            f"G{gear_num}\nk={k}",
            ha="center",
            va="center",
            fontsize=6.5 if gear_num == 1 else 5.5,
            color=pal["text"],
            fontweight="bold" if gear_num == 1 else "normal",
            zorder=8,
        )

    if title is None:
        title = (
            f"Universal π Clock · Hybrid (Egg + Spiral)\n"
            f"{clock.total_ticks:,} ticks · growth={growth:.2f}"
        )
    if title:
        ax.set_title(title, color=pal["text"], fontsize=11, pad=12)


def draw_styled_clock(
    ax: plt.Axes,
    clock: UniversalPiClock,
    *,
    style: str = "egg_of_life",
    theme: str = "dark",
    layout: str = "portrait",
    show_ticks: bool = True,
    show_labels: bool = True,
    show_hands: bool = True,
    slice_lines: int = DEFAULT_SLICE_LINES,
    title: str | None = None,
    growth: float = 1.0,
    **egg_kwargs,
) -> None:
    """Dispatch to the selected visual style."""
    style = (style or "egg_of_life").lower().replace("-", "_")
    if style not in VISUAL_STYLES:
        raise ValueError(f"Unknown style {style!r}; choose from {VISUAL_STYLES}")

    if style == "golden_spiral":
        draw_golden_spiral_clock(
            ax,
            clock,
            theme=theme,
            layout=layout,
            show_ticks=show_ticks,
            show_labels=show_labels,
            show_hands=show_hands,
            slice_lines=slice_lines,
            title=title,
        )
    elif style == "spiral_arms":
        draw_spiral_arms_clock(
            ax,
            clock,
            theme=theme,
            show_ticks=show_ticks,
            show_labels=show_labels,
            show_hands=show_hands,
            slice_lines=slice_lines,
            title=title,
        )
    elif style == "hybrid":
        draw_hybrid_clock(
            ax,
            clock,
            theme=theme,
            show_ticks=show_ticks,
            show_labels=show_labels,
            show_hands=show_hands,
            slice_lines=slice_lines,
            title=title,
            growth=growth,
        )
    else:
        # Lazy import avoid circular issues — egg lives in visualize
        from .visualize import draw_clock as draw_egg

        draw_egg(
            ax,
            clock,
            show_ticks=show_ticks,
            show_labels=show_labels,
            show_hands=show_hands,
            slice_lines=slice_lines,
            title=title,
            **egg_kwargs,
        )


def render_spiral_clock(
    clock: UniversalPiClock,
    *,
    style: str = "golden_spiral",
    theme: str = "dark",
    layout: str = "portrait",
    output: Path | str | None = None,
    dpi: int = 200,
    figsize: tuple[float, float] | None = None,
    show_ticks: bool = True,
    show_labels: bool = True,
    show_hands: bool = True,
    slice_lines: int = DEFAULT_SLICE_LINES,
    title: str | None = None,
    growth: float = 1.0,
    tight_margins: bool = False,
) -> plt.Figure:
    """Render a spiral-style clock face and optionally save PNG."""
    pal = _palette(theme)
    if figsize is None:
        figsize = _figsize_for_layout(layout if style == "golden_spiral" else "square")
        if style == "spiral_arms":
            figsize = (11, 11)
        elif style == "hybrid":
            figsize = (12, 12)

    fig, ax = plt.subplots(figsize=figsize, facecolor=pal["bg"])
    draw_styled_clock(
        ax,
        clock,
        style=style,
        theme=theme,
        layout=layout,
        show_ticks=show_ticks,
        show_labels=show_labels,
        show_hands=show_hands,
        slice_lines=slice_lines,
        title=title,
        growth=growth,
    )
    if tight_margins:
        fig.subplots_adjust(left=0.02, right=0.98, bottom=0.02, top=0.98)
    else:
        fig.tight_layout()
    if output is not None:
        fig.savefig(output, dpi=dpi, facecolor=pal["bg"], bbox_inches="tight")
    return fig
