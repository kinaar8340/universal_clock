"""Universal π Clock — Egg of Life 7-gear sacred geometry timekeeper."""

from .clock import EARTH_DAY_SECONDS, SLICES_PER_GEAR, UniversalPiClock
from .visualize import DEFAULT_SLICE_LINES, GEAR_COLORS, draw_hand, render_clock, render_clock_array

__all__ = [
    "DEFAULT_SLICE_LINES",
    "EARTH_DAY_SECONDS",
    "SLICES_PER_GEAR",
    "UniversalPiClock",
    "GEAR_COLORS",
    "draw_hand",
    "render_clock",
    "render_clock_array",
]

__version__ = "0.2.0"