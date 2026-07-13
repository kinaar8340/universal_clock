"""Universal π Clock — Egg of Life & golden-spiral 7-gear timekeeper."""

from .clock import EARTH_DAY_SECONDS, SLICES_PER_GEAR, UniversalPiClock
from .spiral import (
    B_GOLDEN,
    PHI,
    VISUAL_STYLES,
    spiral_curve,
    spiral_radius,
    spiral_xy,
    theta_for_slice,
)
from .visualize import (
    DEFAULT_SLICE_LINES,
    GEAR_COLORS,
    PETAL_CYCLE_SECONDS,
    PETAL_FRAME_COUNT,
    PETAL_FRAME_SECONDS,
    PETAL_SEGMENT_SECONDS,
    draw_hand,
    petal_color_for_elapsed,
    petal_color_gear,
    petal_frame_index,
    petal_filled_indices,
    petal_subframe_index,
    petal_segment_index,
    render_clock,
    render_clock_array,
)

__all__ = [
    "B_GOLDEN",
    "DEFAULT_SLICE_LINES",
    "PETAL_CYCLE_SECONDS",
    "PETAL_FRAME_COUNT",
    "PETAL_FRAME_SECONDS",
    "PETAL_SEGMENT_SECONDS",
    "EARTH_DAY_SECONDS",
    "PHI",
    "SLICES_PER_GEAR",
    "UniversalPiClock",
    "VISUAL_STYLES",
    "GEAR_COLORS",
    "draw_hand",
    "petal_color_for_elapsed",
    "petal_color_gear",
    "petal_frame_index",
    "petal_filled_indices",
    "petal_subframe_index",
    "petal_segment_index",
    "render_clock",
    "render_clock_array",
    "spiral_curve",
    "spiral_radius",
    "spiral_xy",
    "theta_for_slice",
]

__version__ = "0.3.0"
