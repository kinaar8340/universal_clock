"""Animation helpers for the Universal π Clock."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

from .clock import UniversalPiClock
from .visualize import DEFAULT_SLICE_LINES, _bg_for_theme, _default_figsize, draw_clock


def save_animation_gif(
    *,
    frames: int = 60,
    ticks_per_frame: int = 50,
    start_ticks: int = 0,
    output: Path | str,
    fps: int = 10,
    show_hands: bool = True,
    slice_lines: int = DEFAULT_SLICE_LINES,
    style: str = "egg_of_life",
    theme: str = "dark",
    layout: str = "portrait",
    growth: float = 1.0,
    show_labels: bool = False,
) -> Path:
    """Advance the clock and save an animated GIF."""
    clock = UniversalPiClock()
    if start_ticks:
        clock.fast_forward(start_ticks)

    bg = _bg_for_theme(theme, style)
    figsize = _default_figsize(style, layout, None)
    fig, ax = plt.subplots(figsize=figsize, facecolor=bg)
    output = Path(output)

    # Subtle growth pulse for hybrid style across the animation
    growth_base = growth

    def update(frame: int) -> None:
        clock.tick(ticks_per_frame)
        g = growth_base
        if style == "hybrid":
            # Gentle breath: ±8% over the loop
            g = growth_base * (1.0 + 0.08 * ((frame % 20) / 10.0 - 1.0))
        draw_clock(
            ax,
            clock,
            show_labels=show_labels,
            show_hands=show_hands,
            slice_lines=slice_lines,
            style=style,
            theme=theme,
            layout=layout,
            growth=g,
        )

    draw_clock(
        ax,
        clock,
        show_labels=show_labels,
        show_hands=show_hands,
        slice_lines=slice_lines,
        style=style,
        theme=theme,
        layout=layout,
        growth=growth_base,
    )

    anim = FuncAnimation(fig, update, frames=frames, interval=1000 / fps, blit=False)
    writer = PillowWriter(fps=fps)
    anim.save(output, writer=writer, dpi=120)
    plt.close(fig)
    return output
