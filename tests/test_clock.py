"""Tests for UniversalPiClock carry logic."""

import time
from unittest.mock import patch

from universal_clock import UniversalPiClock
from universal_clock.clock import EARTH_DAY_SECONDS, SLICES_PER_GEAR
from universal_clock.visualize import (
    DEFAULT_SLICE_LINES,
    GEAR_COLORS,
    PETAL_FRAME_COUNT,
    PETAL_FRAME_SECONDS,
    petal_color_for_elapsed,
    petal_color_gear,
    petal_frame_index,
    petal_filled_indices,
    petal_subframe_index,
    petal_segment_index,
    slice_line_step,
)


def test_initial_state():
    clock = UniversalPiClock()
    assert clock.gears == [1] * 7
    assert clock.total_ticks == 0


def test_single_tick():
    clock = UniversalPiClock()
    clock.tick()
    assert clock.gears[0] == 2
    assert clock.gears[1] == 1


def test_poc_5000_ticks():
    clock = UniversalPiClock()
    clock.fast_forward(5000)
    assert clock.gears == [101, 15, 1, 1, 1, 1, 1]
    assert clock.total_ticks == 5000


def test_carry_at_350():
    clock = UniversalPiClock()
    clock.fast_forward(349)
    assert clock.gears[0] == 350
    assert clock.gears[1] == 1
    clock.tick()
    assert clock.gears[0] == 1
    assert clock.gears[1] == 2


def test_earth_rate():
    clock = UniversalPiClock()
    assert clock.set_gear_rate_seconds(86_400) == 86_400 / 350


def test_set_earth_rate():
    clock = UniversalPiClock()
    assert clock.set_earth_rate() == EARTH_DAY_SECONDS / SLICES_PER_GEAR
    assert clock.tick_interval == EARTH_DAY_SECONDS / SLICES_PER_GEAR


def test_tick_realtime_waits():
    clock = UniversalPiClock()
    clock.set_earth_rate(350.0)  # 1 second per tick for easy math
    t0 = 1000.0
    with patch("universal_clock.clock.time.time", side_effect=[t0 + 0.5, t0 + 1.1]):
        clock.last_tick_time = t0
        assert clock.tick_realtime() is False
        assert clock.gears[0] == 1
        clock.last_tick_time = t0
        assert clock.tick_realtime() is True
        assert clock.gears[0] == 2


def test_petal_color_sequence():
    assert petal_segment_index(0) == 0
    assert petal_color_gear(0) == 2
    assert petal_color_for_elapsed(0) == GEAR_COLORS[1]
    assert petal_color_gear(9.9) == 2
    assert petal_color_gear(10) == 3
    assert petal_color_gear(29.9) == 4
    assert petal_color_gear(30) == 5
    assert petal_color_gear(49.9) == 6
    assert petal_color_gear(50) == 7
    assert petal_color_gear(59.9) == 7
    assert petal_color_gear(60) == 2
    assert petal_color_for_elapsed(30) == GEAR_COLORS[4]
    assert petal_color_for_elapsed(50) == GEAR_COLORS[6]


def test_petal_frame_sequence():
    assert PETAL_FRAME_COUNT == 18
    assert PETAL_FRAME_SECONDS == 60 / 18
    assert petal_frame_index(0) == 0
    assert petal_frame_index(3.32) == 0
    assert petal_frame_index(3.34) == 1
    assert petal_frame_index(9.99) == 2
    assert petal_frame_index(10) == 3
    assert petal_frame_index(29.99) == 8
    assert petal_frame_index(59.99) == 17
    assert petal_frame_index(60) == 0
    assert petal_subframe_index(0) == 0
    assert petal_subframe_index(6.67) == 2
    assert petal_subframe_index(10) == 0
    assert petal_filled_indices(0) == frozenset({0, 3})
    assert petal_filled_indices(4) == frozenset({1, 4})
    assert petal_filled_indices(7) == frozenset({2, 5})


def test_slice_line_step_default():
    assert DEFAULT_SLICE_LINES == 70
    assert slice_line_step(70) == 5
    assert slice_line_step(350) == 1


def test_tick_realtime_speed_multiplier():
    clock = UniversalPiClock()
    clock.set_earth_rate(100.0)
    t0 = time.time()
    clock.last_tick_time = t0 - 1.0
    assert clock.tick_realtime(speed_multiplier=100.0) is True

def test_spiral_math():
    from universal_clock.spiral import (
        B_GOLDEN,
        PHI,
        spiral_radius,
        spiral_xy,
        theta_for_slice,
    )
    import math

    assert abs(PHI - (1 + math.sqrt(5)) / 2) < 1e-12
    assert abs(B_GOLDEN - math.log(PHI) / (math.pi / 2)) < 1e-12
    assert theta_for_slice(1) == 0.0
    th_end = theta_for_slice(350)
    assert abs(th_end - 2.0 * 2 * math.pi) < 1e-9
    # r grows by φ every quarter-turn (π/2)
    r0 = float(spiral_radius(0.0, a=1.0))
    r_quarter = float(spiral_radius(math.pi / 2, a=1.0))
    assert abs(r_quarter / r0 - PHI) < 1e-9
    x, y = spiral_xy(0.0, a=1.0)
    assert abs(float(x) - 0.0) < 1e-9
    assert abs(float(y) - 1.0) < 1e-9  # 12 o'clock


def test_render_styles_smoke():
    """Each visual style renders without error and produces a non-empty array."""
    import matplotlib

    matplotlib.use("Agg")
    from universal_clock import UniversalPiClock, render_clock_array
    from universal_clock.spiral import VISUAL_STYLES

    clock = UniversalPiClock()
    clock.fast_forward(5000)
    for style in VISUAL_STYLES:
        arr = render_clock_array(
            clock,
            style=style,
            theme="dark",
            layout="portrait",
            dpi=40,
            figsize=(4, 4) if style != "golden_spiral" else (3, 5),
            show_labels=False,
            title="",
        )
        assert arr.ndim == 3
        assert arr.shape[2] == 3
        assert arr.shape[0] > 10 and arr.shape[1] > 10
