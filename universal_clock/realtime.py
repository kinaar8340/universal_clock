"""Real-time Earth-rate simulation loop."""

from __future__ import annotations

import time

import matplotlib.pyplot as plt

from .clock import UniversalPiClock
from .visualize import DEFAULT_SLICE_LINES, _bg_for_theme, _default_figsize, draw_clock


def run_realtime(
    clock: UniversalPiClock,
    *,
    speed_multiplier: float = 1.0,
    sleep_seconds: float = 0.01,
    figsize: tuple[float, float] | None = None,
    slice_lines: int = DEFAULT_SLICE_LINES,
    style: str = "egg_of_life",
    theme: str = "dark",
    layout: str = "portrait",
    growth: float = 1.0,
) -> None:
    """Run an interactive matplotlib loop driven by tick_realtime()."""
    bg = _bg_for_theme(theme, style)
    fig_size = _default_figsize(style, layout, figsize)
    plt.ion()
    fig, ax = plt.subplots(figsize=fig_size, facecolor=bg)
    try:
        while plt.fignum_exists(fig.number):
            if clock.tick_realtime(speed_multiplier=speed_multiplier):
                # Hybrid growth: nudge outward slightly when G1 carries (k==1 after tick)
                g = growth
                if style == "hybrid" and clock.gears[0] == 1 and clock.total_ticks > 0:
                    g = growth * (1.0 + 0.06 * min(clock.gears[1] - 1, 10))
                draw_clock(
                    ax,
                    clock,
                    slice_lines=slice_lines,
                    style=style,
                    theme=theme,
                    layout=layout,
                    growth=g,
                )
                fig.canvas.draw_idle()
            plt.pause(sleep_seconds)
            if not plt.get_fignums():
                break
    except KeyboardInterrupt:
        pass
    finally:
        plt.ioff()
        if plt.get_fignums():
            plt.show()
