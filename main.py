#!/usr/bin/env python3
"""CLI for the Universal π Clock."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt

from universal_clock import UniversalPiClock, render_clock
from universal_clock.clock import EARTH_DAY_SECONDS
from universal_clock.realtime import run_realtime
from universal_clock.spiral import LAYOUTS, VISUAL_STYLES
from universal_clock.visualize import DEFAULT_SLICE_LINES

DEFAULT_OUTPUT = Path(__file__).resolve().parent / "output" / "egg_of_life_clock.png"


def _print_state(clock: UniversalPiClock, *, output: Path | None = None) -> None:
    print("=== Universal π Clock ===")
    print(f"Total ticks: {clock.total_ticks:,}")
    for i in range(1, 8):
        k = clock.gears[i - 1]
        fill_pct = 100.0 * k / 350
        print(f"  Gear {i}: k={k:3d}  v≈{clock.value(i):6.2f}  ({fill_pct:5.1f}% filled)")
    if output is not None:
        print(f"Image: {output}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Universal π Clock — Egg of Life & golden-spiral 7-gear visualization",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--ticks",
        type=int,
        default=None,
        help="Instant batch: fast-forward N ticks then render (default: 5000 in batch mode)",
    )
    mode.add_argument(
        "--earth-rate",
        action="store_true",
        help="Real-time Earth mode (Gear 1 revolution = 86,400 s)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="PNG output path (batch mode only)",
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=1.0,
        help="Speed multiplier for --earth-rate (e.g. 1000 = 1000× faster)",
    )
    parser.add_argument(
        "--rev-seconds",
        type=float,
        default=EARTH_DAY_SECONDS,
        help="Seconds for one Gear 1 revolution in real-time mode (default: 86400)",
    )
    parser.add_argument(
        "--style",
        choices=list(VISUAL_STYLES),
        default="egg_of_life",
        help="Visual style: egg_of_life | golden_spiral | spiral_arms | hybrid",
    )
    parser.add_argument(
        "--theme",
        choices=["dark", "light"],
        default="dark",
        help="Color theme for spiral styles (default: dark)",
    )
    parser.add_argument(
        "--layout",
        choices=list(LAYOUTS),
        default="portrait",
        help="Layout for golden_spiral style (default: portrait)",
    )
    parser.add_argument(
        "--growth",
        type=float,
        default=1.0,
        help="Spiral growth factor for hybrid style (default: 1.0)",
    )
    parser.add_argument(
        "--no-ticks",
        action="store_true",
        help="Hide radial / spiral slice lines",
    )
    parser.add_argument(
        "--slice-lines",
        type=int,
        default=DEFAULT_SLICE_LINES,
        metavar="N",
        help=f"Slice lines per face (default: {DEFAULT_SLICE_LINES}; must divide 350)",
    )
    parser.add_argument(
        "--no-labels",
        action="store_true",
        help="Hide k/π circumference labels",
    )
    parser.add_argument(
        "--no-hands",
        action="store_true",
        help="Hide moving hand indicators",
    )
    parser.add_argument(
        "--animate",
        type=int,
        default=0,
        metavar="FRAMES",
        help="Save animated GIF with N frames (batch mode only)",
    )
    args = parser.parse_args(argv)

    clock = UniversalPiClock()
    show_hands = not args.no_hands
    show_ticks = not args.no_ticks
    show_labels = not args.no_labels
    slice_lines = args.slice_lines
    style = args.style
    theme = args.theme
    layout = args.layout
    growth = args.growth

    if args.earth_rate:
        sec_per_tick = clock.set_earth_rate(args.rev_seconds)
        effective = sec_per_tick / args.speed
        print("=== Universal π Clock · Real-time Mode ===")
        print(f"Style: {style}  theme={theme}  layout={layout}")
        print(f"Gear 1 revolution: {args.rev_seconds:,.0f} s")
        print(f"Tick interval: {sec_per_tick:.4f} s  (effective {effective:.6f} s @ {args.speed}×)")
        print("Close the plot window or press Ctrl+C to stop.")
        run_realtime(
            clock,
            speed_multiplier=args.speed,
            slice_lines=slice_lines,
            style=style,
            theme=theme,
            layout=layout,
            growth=growth,
        )
        _print_state(clock)
        return 0

    ticks = 5000 if args.ticks is None else args.ticks
    if ticks:
        clock.fast_forward(ticks)

    # Sensible default output name per style
    output = args.output
    if args.output == DEFAULT_OUTPUT and style != "egg_of_life":
        output = args.output.parent / f"{style}_clock.png"

    output.parent.mkdir(parents=True, exist_ok=True)
    fig = render_clock(
        clock,
        output=output,
        show_ticks=show_ticks,
        show_labels=show_labels,
        show_hands=show_hands,
        slice_lines=slice_lines,
        style=style,
        theme=theme,
        layout=layout,
        growth=growth,
    )
    plt.close(fig)

    _print_state(clock, output=output)

    if args.animate > 0:
        from universal_clock.animate import save_animation_gif

        gif_path = output.with_suffix(".gif")
        save_animation_gif(
            start_ticks=max(0, ticks - args.animate * 50),
            frames=args.animate,
            output=gif_path,
            show_hands=show_hands,
            slice_lines=slice_lines,
            style=style,
            theme=theme,
            layout=layout,
            growth=growth,
        )
        print(f"GIF:   {gif_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
