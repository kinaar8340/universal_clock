"""Tests for UniversalPiClock carry logic."""

import time
from unittest.mock import patch

from universal_clock import UniversalPiClock
from universal_clock.clock import EARTH_DAY_SECONDS, SLICES_PER_GEAR
from universal_clock.visualize import DEFAULT_SLICE_LINES, slice_line_step


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