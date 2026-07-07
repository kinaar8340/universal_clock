"""Real-time Earth-rate simulation loop."""

from __future__ import annotations

import time

import matplotlib.pyplot as plt

from .clock import UniversalPiClock
from .visualize import BG_COLOR, draw_clock


def run_realtime(
    clock: UniversalPiClock,
    *,
    speed_multiplier: float = 1.0,
    sleep_seconds: float = 0.01,
    figsize: tuple[float, float] = (10, 10),
) -> None:
    """Run an interactive matplotlib loop driven by tick_realtime()."""
    plt.ion()
    fig, ax = plt.subplots(figsize=figsize, facecolor=BG_COLOR)
    try:
        while plt.fignum_exists(fig.number):
            if clock.tick_realtime(speed_multiplier=speed_multiplier):
                draw_clock(ax, clock)
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