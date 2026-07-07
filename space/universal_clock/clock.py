"""Seven-gear cascading π clock."""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field

SLICES_PER_GEAR = 350
NUM_GEARS = 7
EARTH_DAY_SECONDS = 86_400


@dataclass
class UniversalPiClock:
    """Cascading 7-gear clock with 350 π-labeled slices per gear.

    Gear 1 is the fastest (center circle). Each gear advances one slice per
    carry from the gear below. When a gear completes slice 350 it resets to 1
    and carries +1 to the next higher gear.
    """

    gears: list[int] = field(default_factory=lambda: [1] * NUM_GEARS)
    total_ticks: int = 0
    tick_interval: float | None = None
    last_tick_time: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        if len(self.gears) != NUM_GEARS:
            raise ValueError(f"Expected {NUM_GEARS} gears, got {len(self.gears)}")
        for k in self.gears:
            if not 1 <= k <= SLICES_PER_GEAR:
                raise ValueError(f"Gear slice k must be in [1, {SLICES_PER_GEAR}], got {k}")

    @property
    def values(self) -> list[float]:
        """Current value v = k/π for each gear."""
        return [k / math.pi for k in self.gears]

    def value(self, gear: int) -> float:
        """Value for gear index 1–7."""
        return self.gears[gear - 1] / math.pi

    def tick(self, n: int = 1) -> None:
        """Advance the clock by n ticks on the lowest gear."""
        for _ in range(n):
            self._single_tick()

    def _single_tick(self) -> None:
        carry = True
        gear_idx = 0
        while carry and gear_idx < NUM_GEARS:
            self.gears[gear_idx] += 1
            if self.gears[gear_idx] > SLICES_PER_GEAR:
                self.gears[gear_idx] = 1
                gear_idx += 1
            else:
                carry = False
        self.total_ticks += 1

    def fast_forward(self, ticks: int) -> None:
        """Batch-advance — alias for tick() with explicit fast-mode naming."""
        self.tick(ticks)

    def set_gear_rate_seconds(self, full_revolution_seconds: float) -> float:
        """Seconds per tick when Gear 1 completes one revolution in the given period."""
        return full_revolution_seconds / SLICES_PER_GEAR

    def set_earth_rate(self, full_rev_seconds: float = EARTH_DAY_SECONDS) -> float:
        """Set Gear 1 to complete one revolution in full_rev_seconds (Earth = 86,400)."""
        self.tick_interval = full_rev_seconds / SLICES_PER_GEAR
        self.last_tick_time = time.time()
        return self.tick_interval

    def tick_realtime(self, speed_multiplier: float = 1.0) -> bool:
        """Advance one tick when enough real time has passed. Returns True if ticked."""
        if self.tick_interval is None:
            raise RuntimeError("Call set_earth_rate() before tick_realtime()")
        if speed_multiplier <= 0:
            raise ValueError("speed_multiplier must be positive")
        now = time.time()
        if now - self.last_tick_time >= self.tick_interval / speed_multiplier:
            self.tick()
            self.last_tick_time = now
            return True
        return False

    def state_dict(self) -> dict:
        return {
            "gears": list(self.gears),
            "values": self.values,
            "total_ticks": self.total_ticks,
        }