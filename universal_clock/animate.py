"""Animation helpers for the Universal π Clock."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

from .clock import UniversalPiClock
from .visualize import render_clock


def save_animation_gif(
    *,
    frames: int = 60,
    ticks_per_frame: int = 50,
    start_ticks: int = 0,
    output: Path | str,
    fps: int = 10,
    show_hands: bool = True,
) -> Path:
    """Advance the clock and save an animated GIF."""
    clock = UniversalPiClock()
    if start_ticks:
        clock.fast_forward(start_ticks)

    fig, ax = plt.subplots(figsize=(10, 10), facecolor="#0d1117")
    output = Path(output)

    def update(_frame: int) -> None:
        clock.tick(ticks_per_frame)
        from .visualize import draw_clock

        draw_clock(ax, clock, show_labels=False, show_hands=show_hands)

    draw_clock(ax, clock, show_labels=False, show_hands=show_hands)

    anim = FuncAnimation(fig, update, frames=frames, interval=1000 / fps, blit=False)
    writer = PillowWriter(fps=fps)
    anim.save(output, writer=writer, dpi=120)
    plt.close(fig)
    return output